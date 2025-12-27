"""Tests for BaseClient.auto_paginate method."""

import os
from typing import TypedDict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.base import BaseClient


class MockResponse(TypedDict):
    """Test response type for auto-pagination tests."""

    title: str
    id: int


class MockClient(BaseClient):
    """Testable subclass of BaseClient for direct testing."""

    pass


@pytest.mark.asyncio
async def test_auto_paginate_single_page():
    """Test auto-pagination with a single page of results."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Item 1", "id": 1},
        {"title": "Item 2", "id": 2},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "2",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client_class,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        client = MockClient()
        result = await client.auto_paginate(
            "/test/endpoint", response_type=MockResponse, params={"limit": 2}
        )

        # Should return all items from single page
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "Item 1"
        assert result[1]["title"] == "Item 2"

        # Should only make one request
        assert mock_instance.get.call_count == 1


@pytest.mark.asyncio
async def test_auto_paginate_multiple_pages():
    """Test auto-pagination across multiple pages."""
    # Mock first page
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [
        {"title": "Item 1", "id": 1},
        {"title": "Item 2", "id": 2},
    ]
    mock_response_page1.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "5",
    }
    mock_response_page1.raise_for_status = MagicMock()

    # Mock second page
    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = [
        {"title": "Item 3", "id": 3},
        {"title": "Item 4", "id": 4},
    ]
    mock_response_page2.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "5",
    }
    mock_response_page2.raise_for_status = MagicMock()

    # Mock third page (last page with 1 item)
    mock_response_page3 = MagicMock()
    mock_response_page3.json.return_value = [
        {"title": "Item 5", "id": 5},
    ]
    mock_response_page3.headers = {
        "X-Pagination-Page": "3",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "5",
    }
    mock_response_page3.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client_class,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(
            side_effect=[mock_response_page1, mock_response_page2, mock_response_page3]
        )
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        client = MockClient()
        result = await client.auto_paginate(
            "/test/endpoint", response_type=MockResponse, params={"limit": 2}
        )

        # Should return all items from all pages
        assert isinstance(result, list)
        assert len(result) == 5
        assert result[0]["title"] == "Item 1"
        assert result[2]["title"] == "Item 3"
        assert result[4]["title"] == "Item 5"

        # Should make exactly 3 requests (one per page)
        assert mock_instance.get.call_count == 3


@pytest.mark.asyncio
async def test_auto_paginate_empty_results():
    """Test auto-pagination with empty results."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "0",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client_class,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        client = MockClient()
        result = await client.auto_paginate(
            "/test/endpoint", response_type=MockResponse, params={"limit": 10}
        )

        # Should return empty list
        assert isinstance(result, list)
        assert len(result) == 0

        # Should only make one request
        assert mock_instance.get.call_count == 1


@pytest.mark.asyncio
async def test_auto_paginate_uses_server_next_page():
    """Test that auto-pagination uses server-provided next_page property."""
    # Mock first page - server indicates page 5 as next
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [{"title": "Item 1", "id": 1}]
    mock_response_page1.headers = {
        "X-Pagination-Page": "3",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "5",
        "X-Pagination-Item-Count": "5",
    }
    mock_response_page1.raise_for_status = MagicMock()

    # Mock second page - last page
    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = [{"title": "Item 2", "id": 2}]
    mock_response_page2.headers = {
        "X-Pagination-Page": "5",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "5",
        "X-Pagination-Item-Count": "5",
    }
    mock_response_page2.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client_class,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(
            side_effect=[mock_response_page1, mock_response_page2]
        )
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        client = MockClient()
        result = await client.auto_paginate(
            "/test/endpoint", response_type=MockResponse, params={"limit": 1}
        )

        # Should successfully fetch both pages
        assert len(result) == 2

        # Verify the page parameters sent in requests
        calls = mock_instance.get.call_args_list
        assert len(calls) == 2

        # First call should be page 1 (initial page)
        first_call_params = calls[0].kwargs.get("params", {})
        assert first_call_params["page"] == 1

        # Second call should be page 4 (server's next_page from page 3)
        second_call_params = calls[1].kwargs.get("params", {})
        assert second_call_params["page"] == 4


@pytest.mark.asyncio
async def test_auto_paginate_preserves_params():
    """Test that auto-pagination preserves additional query parameters."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{"title": "Item 1", "id": 1}]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client_class,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        client = MockClient()
        result = await client.auto_paginate(
            "/test/endpoint",
            response_type=MockResponse,
            params={"limit": 1, "period": "weekly", "sort": "newest"},
        )

        # Should return results
        assert len(result) == 1

        # Verify params were preserved
        call_params = mock_instance.get.call_args.kwargs.get("params", {})
        assert call_params["limit"] == 1
        assert call_params["period"] == "weekly"
        assert call_params["sort"] == "newest"
        assert call_params["page"] == 1


@pytest.mark.asyncio
async def test_auto_paginate_max_pages_safety_guard():
    """Test that auto-pagination stops at max_pages safety limit."""

    # Create responses that suggest infinite pagination
    def create_mock_response(page_num: int) -> MagicMock:
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"title": f"Item {page_num}", "id": page_num}
        ]
        mock_response.headers = {
            "X-Pagination-Page": str(page_num),
            "X-Pagination-Limit": "1",
            "X-Pagination-Page-Count": "999",  # Very large page count
            "X-Pagination-Item-Count": "999",
        }
        mock_response.raise_for_status = MagicMock()
        return mock_response

    with (
        patch("httpx.AsyncClient") as mock_client_class,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = MagicMock()
        # Create infinite sequence of responses
        mock_instance.get = AsyncMock(
            side_effect=[create_mock_response(i) for i in range(1, 200)]
        )
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        client = MockClient()

        # Should raise RuntimeError when hitting max_pages limit
        with pytest.raises(
            RuntimeError,
            match="Pagination safety limit reached: 5 pages fetched",
        ):
            await client.auto_paginate(
                "/test/endpoint",
                response_type=MockResponse,
                params={"limit": 1},
                max_pages=5,
            )

        # Should have made exactly 5 requests (max_pages)
        assert mock_instance.get.call_count == 5


@pytest.mark.asyncio
async def test_auto_paginate_with_none_params():
    """Test auto-pagination with None params (should use empty dict)."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{"title": "Item 1", "id": 1}]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client_class,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_instance

        client = MockClient()
        result = await client.auto_paginate(
            "/test/endpoint", response_type=MockResponse, params=None
        )

        # Should return results
        assert len(result) == 1

        # Verify params include page even when None was passed
        call_params = mock_instance.get.call_args.kwargs.get("params", {})
        assert call_params["page"] == 1
