"""Authentication client for Trakt API."""

import asyncio
import contextlib
import json
import logging
import os
import threading
import time
import weakref
from http import HTTPStatus
from typing import Final

import httpx
from pydantic import ValidationError

from config.auth import (
    DEVICE_TOKEN_ERROR_MESSAGES,
    DEVICE_TOKEN_OAUTH_ERROR_STATUSES,
    DEVICE_TOKEN_PENDING_STATUS,
    DEVICE_TOKEN_REJECTED_MESSAGE,
    DEVICE_TOKEN_SLOW_DOWN_STATUS,
    INVALID_CLIENT_MESSAGE,
    OAUTH_ERROR_AUTHORIZATION_PENDING,
    OAUTH_ERROR_INVALID_CLIENT,
    OAUTH_ERROR_INVALID_GRANT,
    OAUTH_REDIRECT_URI,
)
from config.endpoints import TRAKT_ENDPOINTS
from models.auth import (
    DeviceTokenRequest,
    OAuthErrorResponse,
    TraktAuthToken,
    TraktDeviceCode,
)
from utils.api.error_types import (
    AuthorizationPendingError,
    DeviceAuthorizationError,
    TraktRateLimitError,
)
from utils.api.errors import (
    InvalidParamsError,
    InvalidRequestError,
    MCPError,
    handle_api_errors,
    http_error_response,
    token_refresh_scope,
)

from ..base import BaseClient

logger = logging.getLogger(__name__)

# User authentication token storage path.
# Default lives under the user's home so the token survives across uvx invocations
# (uvx's CWD is a throwaway temp dir). Override via TRAKT_AUTH_TOKEN_PATH —
# Docker images set it to /data/auth_token.json for volume-based persistence.
AUTH_TOKEN_FILE: Final[str] = os.environ.get(
    "TRAKT_AUTH_TOKEN_PATH",
    os.path.expanduser("~/.trakt-mcp/auth_token.json"),
)


def _oauth_error_body(response: httpx.Response) -> OAuthErrorResponse | None:
    """Parse an OAuth error body; None when it is empty or not a JSON object."""
    if not response.content:
        return None
    try:
        return OAuthErrorResponse.model_validate_json(response.content)
    except ValidationError:
        return None


def _is_invalid_client(
    response: httpx.Response, body: OAuthErrorResponse | None
) -> bool:
    """Trakt rejected the app's client credentials rather than the request."""
    return response.status_code == HTTPStatus.UNAUTHORIZED or (
        body is not None and body.error == OAUTH_ERROR_INVALID_CLIENT
    )


_refresh_locks: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = (
    weakref.WeakKeyDictionary()
)


def _shared_refresh_lock() -> asyncio.Lock:
    """Return the refresh lock shared by every AuthClient on this event loop.

    get_client() builds a new AuthClient per tool call, so a per-instance lock
    would let parallel calls spend the same single-use refresh token.
    """
    loop = asyncio.get_running_loop()
    lock = _refresh_locks.get(loop)
    if lock is None:
        lock = _refresh_locks[loop] = asyncio.Lock()
    return lock


def _device_token_error(error: MCPError) -> MCPError | None:
    """Map a failed device-token poll to the error its HTTP status documents.

    Trakt answers these polls with empty bodies, so the generic HTTP error
    mapping cannot tell "still pending" or "denied" apart from real failures.
    Returns None when the status is outside the device-token contract.
    """
    response = http_error_response(error)
    # The generic handler already recognises an authorization_pending body.
    if response is None or isinstance(error, AuthorizationPendingError):
        return None
    body = _oauth_error_body(response)
    error_code = body.error if body else None
    status: int | None = response.status_code
    if _is_invalid_client(response, body):
        return DeviceAuthorizationError(
            http_status=response.status_code,
            message=INVALID_CLIENT_MESSAGE,
            restart_required=True,
        )
    if status == DEVICE_TOKEN_PENDING_STATUS:
        if not response.content or error_code == OAUTH_ERROR_AUTHORIZATION_PENDING:
            return AuthorizationPendingError()
        status = DEVICE_TOKEN_OAUTH_ERROR_STATUSES.get(error_code or "")
        if status is None:
            return DeviceAuthorizationError(
                http_status=response.status_code,
                message=DEVICE_TOKEN_REJECTED_MESSAGE,
                restart_required=True,
            )
    message = DEVICE_TOKEN_ERROR_MESSAGES.get(status)
    if message is None:
        return None
    rate_limited = isinstance(error, TraktRateLimitError)
    return DeviceAuthorizationError(
        http_status=status,
        message=message,
        restart_required=status != DEVICE_TOKEN_SLOW_DOWN_STATUS,
        retry_after=error.retry_after if rate_limited else None,
    )


class AuthClient(BaseClient):
    """Client for handling Trakt authentication."""

    def __init__(self):
        """Initialize the authentication client."""
        super().__init__()
        # Guards all mutations to self.auth_token / self.headers["Authorization"].
        # Used by both clear_auth_token (sync) and refresh_access_token (async,
        # but never held across an await) to prevent interleaved writes.
        self._token_lock: threading.Lock = threading.Lock()
        # Try to load auth token if exists
        self.auth_token: TraktAuthToken | None = self._load_auth_token()
        # True while self.auth_token is the copy in AUTH_TOKEN_FILE. If the file
        # then disappears, clear_auth ran elsewhere and must not be undone.
        self._token_persisted: bool = self.auth_token is not None
        if self.auth_token:
            self._update_headers_with_token()

    def _load_auth_token(self) -> TraktAuthToken | None:
        """Load authentication token from storage."""
        if os.path.exists(AUTH_TOKEN_FILE):
            try:
                with open(AUTH_TOKEN_FILE, encoding="utf-8") as f:
                    token_data = json.load(f)
                    return TraktAuthToken.model_validate(token_data)
            except Exception:
                logger.exception("Error loading auth token from %s", AUTH_TOKEN_FILE)
        return None

    def _save_auth_token(self, token: TraktAuthToken) -> None:
        """Save authentication token to storage."""
        # Create file with secure permissions (user read/write only) using
        # an atomic write-then-replace to avoid partial files.
        # Ensure parent directory exists if there is one
        parent_dir = os.path.dirname(AUTH_TOKEN_FILE)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        tmp_path = f"{AUTH_TOKEN_FILE}.tmp"
        fd = os.open(tmp_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        try:
            try:
                file_obj = os.fdopen(fd, "w", encoding="utf-8")
            except Exception:
                with contextlib.suppress(OSError):
                    os.close(fd)
                raise
            with file_obj:
                file_obj.write(token.model_dump_json())
                file_obj.flush()
                # fsync may not be available on all file objects or platforms
                with contextlib.suppress(OSError, AttributeError, TypeError):
                    os.fsync(file_obj.fileno())
            os.replace(tmp_path, AUTH_TOKEN_FILE)
            self._token_persisted = True
        except Exception:
            with contextlib.suppress(OSError):
                os.remove(tmp_path)
            raise

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        if not self.auth_token:
            return False

        # Check if token is expired
        expiry = self.get_token_expiry()
        return expiry is not None and int(time.time()) < expiry

    def get_token_expiry(self) -> int | None:
        """Get the expiry timestamp of the current token."""
        if not self.auth_token:
            return None
        return self.auth_token.created_at + self.auth_token.expires_in

    def _with_client_secret(self, data: dict[str, str]) -> dict[str, str]:
        """Add the deprecated client_secret to an OAuth body when configured."""
        if self.client_secret:
            return {**data, "client_secret": self.client_secret}
        return data

    @handle_api_errors
    async def get_device_code(self) -> TraktDeviceCode:
        """Get a device code for authentication.

        Returns:
            Device code response from Trakt
        """
        data = {
            "client_id": self.client_id,
        }
        try:
            return await self._post_typed_request(
                TRAKT_ENDPOINTS["device_code"], data, response_type=TraktDeviceCode
            )
        except MCPError as error:
            response = http_error_response(error)
            if response is None or not _is_invalid_client(
                response, _oauth_error_body(response)
            ):
                raise
            raise InvalidRequestError(INVALID_CLIENT_MESSAGE) from error

    @handle_api_errors
    async def get_device_token(self, device_code: str) -> TraktAuthToken:
        """Exchange device code for an access token.

        Args:
            device_code: The device code to exchange

        Returns:
            Authentication token

        Raises:
            AuthorizationPendingError: The user has not approved the code yet.
            DeviceAuthorizationError: Trakt reported an invalid, used, expired
                or denied code, or asked to slow down.
            MCPError: Any other failure, as mapped by handle_api_errors.
        """
        # Validate input with Pydantic
        payload = DeviceTokenRequest.model_validate({"code": device_code})
        data = self._with_client_secret(
            {"code": payload.code, "client_id": self.client_id}
        )

        try:
            token = await self._post_typed_request(
                TRAKT_ENDPOINTS["device_token"], data, response_type=TraktAuthToken
            )
        except MCPError as error:
            mapped = _device_token_error(error)
            if mapped is None:
                raise
            raise mapped from error
        with self._token_lock:
            self._save_auth_token(token)
            self.auth_token = token
            self._update_headers_with_token()
        return token

    async def refresh_access_token(
        self, rejected_access_token: str | None = None
    ) -> bool:
        """Refresh the access token using the stored refresh token.

        Exchanges the refresh_token for a new access_token via the Trakt
        OAuth token endpoint. On success, saves the new token pair to disk.

        Thread-safe: Uses an async lock to prevent concurrent refresh attempts
        from racing and invalidating each other's tokens.

        Args:
            rejected_access_token: Access token the API just rejected with 401.
                When given, refresh even if the token looks unexpired locally
                (server-side revocation, clock skew), unless another call has
                already replaced it.

        Returns:
            True if refresh succeeded, False if refresh failed
        """
        async with _shared_refresh_lock():
            with token_refresh_scope():
                return await self._refresh_holding_lock(rejected_access_token)

    async def _refresh_holding_lock(self, rejected_access_token: str | None) -> bool:
        """Refresh the token; the caller holds the shared refresh lock."""
        # Another AuthClient may have refreshed while we waited; its pair
        # is on disk, and our in-memory refresh token is already spent.
        stored = self._load_auth_token()
        with self._token_lock:
            if stored is None and self._token_persisted:
                # clear_auth ran in another tool call; refreshing would quietly
                # sign the user back in.
                self._forget_token()
                return False
            if stored is not None and (
                self.auth_token is None
                or stored.refresh_token != self.auth_token.refresh_token
            ):
                self.auth_token = stored
                self._update_headers_with_token()
            auth_snapshot = self.auth_token

        # Re-check after acquiring lock — another coroutine may have refreshed
        if rejected_access_token is None:
            if self.is_authenticated():
                return True
        elif (
            auth_snapshot is not None
            and auth_snapshot.access_token != rejected_access_token
        ):
            return True

        if not auth_snapshot or not auth_snapshot.refresh_token:
            return False

        data = self._with_client_secret(
            {
                "refresh_token": auth_snapshot.refresh_token,
                "client_id": self.client_id,
                "redirect_uri": OAUTH_REDIRECT_URI,
                "grant_type": "refresh_token",
            }
        )

        try:
            token = await self._post_typed_request(
                TRAKT_ENDPOINTS["token"], data, response_type=TraktAuthToken
            )
            with self._token_lock:
                if self._token_persisted and not os.path.exists(AUTH_TOKEN_FILE):
                    # Logged out while the refresh was in flight; honour that.
                    self._forget_token()
                    return False
                self._save_auth_token(token)
                self.auth_token = token
                self._update_headers_with_token()
            logger.info("Successfully refreshed access token")
            return True
        except (InvalidRequestError, InvalidParamsError) as error:
            # Only invalid_grant means the token itself is dead; Trakt also sends
            # it for wrong client credentials, and revokes the token when it
            # does. Anything else (e.g. invalid_request for a malformed
            # TRAKT_REDIRECT_URI) leaves it usable, and clearing it would force a
            # reconnect, which costs a Community App connection.
            response = http_error_response(error)
            body = _oauth_error_body(response) if response is not None else None
            if body is None or body.error != OAUTH_ERROR_INVALID_GRANT:
                logger.warning(
                    "Refresh request rejected (HTTP %s); keeping refresh token."
                    + " Check TRAKT_CLIENT_ID and TRAKT_REDIRECT_URI.",
                    response.status_code if response else "unknown",
                )
                return False
            # invalid_grant: Trakt has revoked or consumed this refresh token.
            logger.warning(
                "Refresh token rejected by server, clearing stale token",
                exc_info=True,
            )
            self.clear_auth_token()
            return False
        except (MCPError, OSError, ValueError):
            # Transient / local errors: InternalError (network/timeout),
            # OSError (file I/O), ValueError (validation).
            # Keep the refresh token so the next attempt can succeed.
            logger.warning(
                "Failed to refresh access token (transient"
                + " error), keeping refresh token for next attempt",
                exc_info=True,
            )
            return False

    async def ensure_authenticated(self) -> bool:
        """Ensure the client is authenticated, refreshing the token if needed.

        Checks authentication status and attempts a token refresh when the
        access token has expired but a refresh token is available.

        Returns:
            True if authenticated (possibly after refresh), False otherwise
        """
        if self.is_authenticated():
            return True

        # Token exists but expired — try refreshing
        if self.auth_token and self.auth_token.refresh_token:
            return await self.refresh_access_token()

        return False

    def _forget_token(self) -> None:
        """Drop the in-memory token and its header; caller holds _token_lock."""
        self.auth_token = None
        self._token_persisted = False
        self.headers.pop("Authorization", None)

    def clear_auth_token(self) -> bool:
        """Clear the stored authentication token.

        Thread-safe: Uses a lock to prevent race conditions when multiple
        concurrent 401 responses trigger token clearing.

        Returns:
            True if token was cleared, False if no token existed or already cleared
        """
        with self._token_lock:
            # Early exit if already cleared by another concurrent call
            if self.auth_token is None:
                return False

            # Always clear in-memory state first
            # (handles case where file was deleted externally)
            self._forget_token()

            # Attempt to remove file (suppress if already deleted)
            try:
                os.remove(AUTH_TOKEN_FILE)
            except FileNotFoundError:
                pass
            except OSError:
                logger.warning(
                    "Failed to remove auth token file %s; orphaned file may remain",
                    AUTH_TOKEN_FILE,
                    exc_info=True,
                )

            logger.debug("Cleared authentication token and Authorization header")
            return True
