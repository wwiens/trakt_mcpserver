"""Tests for the process-wide token store and cross-process coordination."""

import asyncio
import os
import time
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import client.auth.client as auth_client_module
from client.auth.client import AuthClient
from client.auth.token_store import TokenStore
from models.auth import TraktAuthToken


def _token(name: str, *, expired: bool = False) -> TraktAuthToken:
    created_at = int(time.time()) - (2 * 604800 if expired else 0)
    return TraktAuthToken(
        access_token=f"{name}_access",
        refresh_token=f"{name}_refresh",
        expires_in=604800,
        created_at=created_at,
    )


def _token_response(token: TraktAuthToken) -> MagicMock:
    response = MagicMock()
    response.json.return_value = token.model_dump()
    response.raise_for_status = MagicMock()
    return response


@pytest.fixture
def token_path() -> Generator[str, None, None]:
    path = auth_client_module.AUTH_TOKEN_FILE
    yield path
    for leftover in (path, f"{path}.lock"):
        if os.path.exists(leftover):
            os.remove(leftover)


@pytest.fixture
def http_post() -> Generator[AsyncMock, None, None]:
    with patch("httpx.AsyncClient") as mock_client:
        instance = MagicMock()
        instance.post = AsyncMock()
        instance.aclose = AsyncMock()
        mock_client.return_value = instance
        yield instance.post


def _write(path: str, token: TraktAuthToken) -> None:
    with open(path, "w", encoding="utf-8") as token_file:
        token_file.write(token.model_dump_json())


def _sent_refresh_token(post: AsyncMock) -> str:
    return post.call_args.kwargs["json"]["refresh_token"]


class TestUnsavedPairSurvives:
    @pytest.mark.asyncio
    async def test_unsaved_pair_is_used_for_the_next_refresh(
        self, token_path: str, http_post: AsyncMock
    ) -> None:
        """A failed save leaves spent pair A on disk; B must not be replaced."""
        _write(token_path, _token("a", expired=True))
        http_post.return_value = _token_response(_token("b", expired=True))
        client = AuthClient()

        with patch.object(client._store, "_write", side_effect=OSError("read-only")):  # pyright: ignore[reportPrivateUsage]
            assert await client.ensure_authenticated() is True

        http_post.return_value = _token_response(_token("c"))
        next_call = AuthClient()
        assert await next_call.ensure_authenticated() is True

        assert _sent_refresh_token(http_post) == "b_refresh"
        assert next_call.auth_token is not None
        assert next_call.auth_token.access_token == "c_access"

    @pytest.mark.asyncio
    async def test_device_token_kept_when_save_fails(
        self, token_path: str, http_post: AsyncMock
    ) -> None:
        """The device code is used up; losing the pair would force a new login."""
        http_post.return_value = _token_response(_token("device"))
        client = AuthClient()

        with patch.object(client._store, "_write", side_effect=OSError("read-only")):  # pyright: ignore[reportPrivateUsage]
            await client.get_device_token("device_code_123")

        assert AuthClient().is_authenticated() is True

    def test_logout_elsewhere_is_seen_for_an_unsaved_pair(
        self, token_path: str
    ) -> None:
        _write(token_path, _token("a"))
        store = TokenStore(token_path)
        store.sync_from_disk()
        with patch.object(store, "_write", side_effect=OSError("read-only")):
            store.save(_token("b"))

        os.remove(token_path)
        store.sync_from_disk()

        assert store.token is None


class TestCrossProcessRefresh:
    @pytest.mark.asyncio
    async def test_second_process_adopts_first_process_pair(
        self, token_path: str, http_post: AsyncMock
    ) -> None:
        """Two stores on one file stand in for two server processes; only the
        file lock serialises them, and the refresh token is spent once."""
        _write(token_path, _token("a", expired=True))

        async def slow_refresh(*args: object, **kwargs: object) -> MagicMock:
            await asyncio.sleep(0.05)
            return _token_response(_token("b"))

        http_post.side_effect = slow_refresh
        first = AuthClient()
        second = AuthClient()
        second._store = TokenStore(token_path)  # pyright: ignore[reportPrivateUsage]
        second._store.sync_from_disk()  # pyright: ignore[reportPrivateUsage]

        results = await asyncio.gather(
            first.ensure_authenticated(), second.ensure_authenticated()
        )

        assert results == [True, True]
        assert http_post.call_count == 1
        for client in (first, second):
            assert client.auth_token is not None
            assert client.auth_token.access_token == "b_access"
        assert os.path.exists(token_path)
