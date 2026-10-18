"""Process-wide owner of the OAuth token pair and its file on disk.

get_client() builds a new AuthClient for every tool call, so the token cannot
live on the client: a pair kept only on one instance would be lost when that
call ends. Every AuthClient in the process shares one TokenStore per token
path instead, and other server processes are coordinated through the file.
"""

import asyncio
import contextlib
import json
import logging
import os
import tempfile
import weakref
from collections.abc import AsyncGenerator
from typing import IO, Final

from models.auth import TraktAuthToken

try:
    import fcntl
except ImportError:  # Windows: refreshes are serialised within a process only
    fcntl = None

logger = logging.getLogger(__name__)

_LOCK_SUFFIX: Final[str] = ".lock"
_FILE_MODE: Final[int] = 0o600


class TokenStore:
    """Holds the current token pair and keeps it in step with the token file."""

    def __init__(self, path: str) -> None:
        """Create a store for the token file at ``path``.

        Args:
            path: Location of the persisted token pair
        """
        self.path = path
        self.token: TraktAuthToken | None = None
        # What the file held when this process last read or wrote it. Only a
        # difference from this means another process changed the file; a stale
        # file after a failed save must not replace the newer pair in memory.
        self._last_seen_on_disk: TraktAuthToken | None = None
        self._refresh_locks: weakref.WeakKeyDictionary[
            asyncio.AbstractEventLoop, asyncio.Lock
        ] = weakref.WeakKeyDictionary()

    def sync_from_disk(self) -> None:
        """Pick up a login, refresh or logout another process made."""
        if not os.path.exists(self.path):
            if self._last_seen_on_disk is not None:
                # The file this process saw was deleted: clear_auth ran elsewhere.
                self.token = None
                self._last_seen_on_disk = None
            return
        on_disk = self._read()
        if on_disk is None or on_disk == self._last_seen_on_disk:
            return
        self.token = on_disk
        self._last_seen_on_disk = on_disk

    def save(self, token: TraktAuthToken) -> None:
        """Make ``token`` current and persist it.

        The pair is kept in memory even if writing fails: once Trakt has issued
        it, the previous refresh token is spent and cannot be used again.
        """
        self.token = token
        try:
            self._write(token)
        except OSError:
            logger.error(
                "Could not save the Trakt token to %s; it is kept in memory"
                + " until this server process stops",
                self.path,
                exc_info=True,
            )
            return
        self._last_seen_on_disk = token

    def clear(self) -> bool:
        """Forget the token pair and delete the token file.

        Returns:
            True if there was a token to clear
        """
        had_token = self.token is not None
        self.token = None
        self._last_seen_on_disk = None
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass
        except OSError:
            logger.warning(
                "Failed to remove auth token file %s; orphaned file may remain",
                self.path,
                exc_info=True,
            )
            # Treat the undeletable file as already seen, so the next sync does
            # not load it again and quietly undo the logout in this process.
            self._last_seen_on_disk = self._read()
        return had_token

    @contextlib.asynccontextmanager
    async def refresh_lock(self) -> AsyncGenerator[None]:
        """Serialise refreshes across this process and other server processes.

        A refresh token is single-use, so two refreshes racing with the same one
        would make Trakt reject (and revoke) the loser.
        """
        loop = asyncio.get_running_loop()
        loop_lock = self._refresh_locks.get(loop)
        if loop_lock is None:
            loop_lock = self._refresh_locks[loop] = asyncio.Lock()
        async with loop_lock:
            lock_file = await asyncio.to_thread(self._acquire_file_lock)
            try:
                yield
            finally:
                self._release_file_lock(lock_file)

    def _read(self) -> TraktAuthToken | None:
        try:
            with open(self.path, encoding="utf-8") as token_file:
                return TraktAuthToken.model_validate(json.load(token_file))
        except (OSError, ValueError) as error:
            # Checked on every tool call, so no traceback; clear_auth removes it.
            logger.warning(
                "Ignoring unreadable auth token file %s: %s", self.path, error
            )
            return None

    def _write(self, token: TraktAuthToken) -> None:
        """Atomically replace the token file, readable by the owner only."""
        directory = os.path.dirname(self.path) or "."
        os.makedirs(directory, exist_ok=True)
        # A unique temp name, so concurrent writers never share a temp file.
        fd, tmp_path = tempfile.mkstemp(
            dir=directory, prefix=f".{os.path.basename(self.path)}."
        )
        try:
            os.chmod(tmp_path, _FILE_MODE)
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(token.model_dump_json())
                tmp_file.flush()
                with contextlib.suppress(OSError, AttributeError, TypeError):
                    os.fsync(tmp_file.fileno())
            os.replace(tmp_path, self.path)
        except BaseException:
            with contextlib.suppress(OSError):
                os.remove(tmp_path)
            raise

    def _acquire_file_lock(self) -> IO[str] | None:
        if fcntl is None:
            return None
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            lock_file = open(f"{self.path}{_LOCK_SUFFIX}", "a", encoding="utf-8")  # noqa: SIM115
        except OSError:
            logger.warning(
                "Cannot open token lock file; refreshes are not coordinated"
                + " with other server processes",
                exc_info=True,
            )
            return None
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        return lock_file

    def _release_file_lock(self, lock_file: IO[str] | None) -> None:
        if lock_file is None or fcntl is None:
            return
        with contextlib.suppress(OSError):
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()


_stores: dict[str, TokenStore] = {}


def get_token_store(path: str) -> TokenStore:
    """Return the process-wide store for the token file at ``path``."""
    store = _stores.get(path)
    if store is None:
        store = _stores[path] = TokenStore(path)
    return store
