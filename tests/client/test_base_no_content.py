"""Tests for BaseClient handling of 204 No Content on GET requests."""

import os
from collections.abc import Generator
from unittest.mock import patch

import httpx
import pytest

from client.base import BaseClient
from utils.api.error_types import TraktResourceNotFoundError
from utils.api.request_context import clear_current_context


@pytest.fixture(autouse=True)
def isolated_context() -> Generator[None, None, None]:
    clear_current_context()
    yield
    clear_current_context()


def _client_returning(status: int, body: bytes = b"") -> BaseClient:
    """Build a BaseClient whose HTTP layer always answers with ``status``."""
    transport = httpx.MockTransport(
        lambda request: httpx.Response(status, content=body, request=request)
    )
    with patch.dict(os.environ, {"TRAKT_CLIENT_ID": "test_id"}):
        client = BaseClient()
    client._client = httpx.AsyncClient(  # pyright: ignore[reportPrivateUsage]
        base_url=client.BASE_URL, transport=transport
    )
    return client


@pytest.mark.asyncio
async def test_get_no_content_raises_not_found() -> None:
    """Trakt answers missing seasons, ratings and stats with an empty 204."""
    client = _client_returning(204)

    with pytest.raises(TraktResourceNotFoundError) as exc_info:
        await client._make_request(  # pyright: ignore[reportPrivateUsage]
            "GET", "/shows/breaking-bad/seasons/99/info"
        )

    assert "/shows/breaking-bad/seasons/99/info" in exc_info.value.message
    assert "Invalid response format" not in exc_info.value.message
    assert exc_info.value.data is not None
    assert exc_info.value.data["resource_type"] == "show"
    assert exc_info.value.data["resource_id"] == "breaking-bad"


@pytest.mark.asyncio
async def test_get_with_body_still_returns_json() -> None:
    client = _client_returning(200, b'{"number": 1}')

    result = await client._make_request(  # pyright: ignore[reportPrivateUsage]
        "GET", "/shows/breaking-bad/seasons/1/info"
    )

    assert result == {"number": 1}
