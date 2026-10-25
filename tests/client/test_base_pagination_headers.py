# pyright: reportPrivateUsage=false
"""Tests for BaseClient._extract_pagination_headers."""

import httpx
import pytest

from client.base import BaseClient


class StubClient(BaseClient):
    """Stub subclass of BaseClient for direct testing."""


def _response(limit: str, item_count: str) -> httpx.Response:
    return httpx.Response(
        200,
        headers={
            "X-Pagination-Page": "1",
            "X-Pagination-Limit": limit,
            "X-Pagination-Page-Count": "1",
            "X-Pagination-Item-Count": item_count,
        },
    )


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> StubClient:
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    return StubClient()


def test_zero_limit_on_empty_result_is_raised_to_one(client: StubClient) -> None:
    """Trakt reports limit 0 for an empty watchlist fetched without page/limit."""
    pagination = client._extract_pagination_headers(_response("0", "0"))

    assert pagination.items_per_page == 1
    assert pagination.total_items == 0
    assert pagination.next_page() is None


def test_zero_limit_with_items_is_rejected(client: StubClient) -> None:
    """A zero page size alongside real items is a bad header, not the quirk."""
    with pytest.raises(ValueError, match="Invalid pagination headers"):
        client._extract_pagination_headers(_response("0", "5"))


def test_negative_limit_on_empty_result_is_rejected(client: StubClient) -> None:
    """Only the zero-limit quirk is tolerated, not any invalid limit."""
    with pytest.raises(ValueError, match="Invalid pagination headers"):
        client._extract_pagination_headers(_response("-5", "0"))
