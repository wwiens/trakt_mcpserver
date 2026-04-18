"""Tests for the process-wide client pool."""
# pyright: reportPrivateUsage=false

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio

from client import pool
from client.auth import AuthClient
from client.pool import (
    get_client,
    get_or_create_shared_http,
    shutdown_clients,
)
from client.search.client import SearchClient
from client.shows.client import ShowsClient
from client.user.client import UserClient
from models.auth import TraktAuthToken

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator
    from pathlib import Path


@pytest_asyncio.fixture(autouse=True)
async def _reset_pool_state() -> AsyncGenerator[None, None]:  # pyright: ignore[reportUnusedFunction]
    """Close and reset pool state around each test.

    Uses ``shutdown_clients`` on both setup and teardown so any real
    ``httpx.AsyncClient`` created during the test is properly closed
    rather than orphaned.
    """
    await shutdown_clients()
    try:
        yield
    finally:
        await shutdown_clients()


@pytest.fixture
def _token_file(tmp_path: Path) -> Generator[Path, None, None]:  # pyright: ignore[reportUnusedFunction]
    """Isolate `auth_token.json` to a per-test temp path."""
    path = tmp_path / "auth_token.json"
    with (
        patch.dict(os.environ, {"TRAKT_AUTH_TOKEN_PATH": str(path)}),
        patch("client.auth.client.AUTH_TOKEN_FILE", str(path)),
    ):
        yield path


def _write_token(path: Path, access_token: str) -> None:
    token = TraktAuthToken(
        access_token=access_token,
        refresh_token="refresh",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )
    path.write_text(token.model_dump_json())


def test_non_auth_client_is_cached_singleton(trakt_env: None) -> None:
    first = get_client(SearchClient)
    second = get_client(SearchClient)
    assert first is second
    assert first._persistent is True
    assert first._owns_client is False


def test_get_client_returns_subclass_type(trakt_env: None) -> None:
    client = get_client(ShowsClient)
    assert isinstance(client, ShowsClient)


def test_auth_client_is_fresh_per_call(trakt_env: None, _token_file: Path) -> None:
    first = get_client(UserClient)
    second = get_client(UserClient)
    assert first is not second
    # Auth wrappers use the shared httpx client but are not cached.
    assert first._persistent is True
    assert first._owns_client is False
    assert UserClient not in pool._CACHE
    assert AuthClient not in pool._CACHE


def test_auth_client_shares_httpx_with_non_auth(
    trakt_env: None, _token_file: Path
) -> None:
    user = get_client(UserClient)
    shows = get_client(ShowsClient)
    assert user._client is shows._client
    assert isinstance(user._client, httpx.AsyncClient)


def test_auth_subclass_reloads_token_from_disk(
    trakt_env: None, _token_file: Path
) -> None:
    _write_token(_token_file, "first_token")
    first = get_client(UserClient)
    assert first.auth_token is not None
    assert first.auth_token.access_token == "first_token"

    _write_token(_token_file, "second_token")
    second = get_client(UserClient)
    assert second.auth_token is not None
    assert second.auth_token.access_token == "second_token"


def test_pooled_clients_share_httpx(trakt_env: None) -> None:
    shows = get_client(ShowsClient)
    search = get_client(SearchClient)
    assert shows._client is search._client
    assert isinstance(shows._client, httpx.AsyncClient)


@pytest.mark.asyncio
async def test_shutdown_clients_closes_shared_http_and_clears_cache(
    trakt_env: None,
) -> None:
    get_client(ShowsClient)
    shared = pool._shared_http
    assert shared is not None
    assert ShowsClient in pool._CACHE

    with patch.object(shared, "aclose", new_callable=AsyncMock) as mock_close:
        await shutdown_clients()

    mock_close.assert_awaited_once()
    assert pool._CACHE == {}
    assert pool._shared_http is None


@pytest.mark.asyncio
async def test_shutdown_allows_shared_http_to_recreate(trakt_env: None) -> None:
    first = get_or_create_shared_http()
    await shutdown_clients()
    second = get_or_create_shared_http()
    assert first is not second


def test_non_pooled_client_path_unchanged(trakt_env: None) -> None:
    direct = ShowsClient()
    assert direct._persistent is False
    assert direct._owns_client is True
    assert direct._client is None
