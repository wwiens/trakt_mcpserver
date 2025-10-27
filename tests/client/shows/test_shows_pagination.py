"""Tests for show client pagination functionality."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.shows.popular import PopularShowsClient
from client.shows.stats import ShowStatsClient
from client.shows.trending import TrendingShowsClient
from models.types.pagination import PaginatedResponse


@pytest.mark.asyncio
async def test_trending_shows_no_page_returns_all():
    """Test that trending shows with no page parameter auto-paginates all results."""
    # Mock first page response
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [
        {"watchers": 100, "show": {"title": "Show 1", "year": 2024}},
        {"watchers": 90, "show": {"title": "Show 2", "year": 2024}},
    ]
    mock_response_page1.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "4",
    }
    mock_response_page1.raise_for_status = MagicMock()

    # Mock second page response
    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = [
        {"watchers": 80, "show": {"title": "Show 3", "year": 2024}},
        {"watchers": 70, "show": {"title": "Show 4", "year": 2024}},
    ]
    mock_response_page2.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "4",
    }
    mock_response_page2.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(
            side_effect=[mock_response_page1, mock_response_page2]
        )
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = TrendingShowsClient()
        result = await client.get_trending_shows(limit=2, page=None)

        # Should return a plain list with all 4 shows
        assert isinstance(result, list)
        assert len(result) == 4
        show_0 = result[0].get("show")
        assert show_0 is not None
        assert show_0["title"] == "Show 1"
        show_3 = result[3].get("show")
        assert show_3 is not None
        assert show_3["title"] == "Show 4"


@pytest.mark.asyncio
async def test_trending_shows_with_page_returns_paginated():
    """Test that trending shows with page parameter returns PaginatedResponse."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watchers": 100, "show": {"title": "Show 1", "year": 2024}},
        {"watchers": 90, "show": {"title": "Show 2", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "4",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = TrendingShowsClient()
        result = await client.get_trending_shows(limit=2, page=1)

        # Should return PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert result.pagination.current_page == 1
        assert result.pagination.total_pages == 2
        assert result.pagination.total_items == 4


@pytest.mark.asyncio
async def test_trending_shows_pagination_metadata():
    """Test that pagination metadata is correctly parsed and exposed."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watchers": 80, "show": {"title": "Show 3", "year": 2024}},
        {"watchers": 70, "show": {"title": "Show 4", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "6",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = TrendingShowsClient()
        result = await client.get_trending_shows(limit=2, page=2)

        # Check metadata properties
        assert result.pagination.current_page == 2
        assert result.pagination.items_per_page == 2
        assert result.pagination.total_pages == 3
        assert result.pagination.total_items == 6


@pytest.mark.asyncio
async def test_trending_shows_navigation_properties():
    """Test that navigation properties work correctly."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watchers": 80, "show": {"title": "Show 3", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "3",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = TrendingShowsClient()
        result = await client.get_trending_shows(limit=1, page=2)

        # Check navigation properties
        assert result.pagination.has_previous_page
        assert result.pagination.has_next_page
        assert result.pagination.previous_page == 1
        assert result.pagination.next_page == 3


@pytest.mark.asyncio
async def test_popular_shows_no_page_returns_all():
    """Test that popular shows with no page parameter auto-paginates."""
    # Mock single page response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Popular 1", "year": 2024},
        {"title": "Popular 2", "year": 2024},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "2",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = PopularShowsClient()
        result = await client.get_popular_shows(limit=2, page=None)

        # Should return a plain list
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "Popular 1"


@pytest.mark.asyncio
async def test_popular_shows_with_page_returns_paginated():
    """Test that popular shows with page parameter returns PaginatedResponse."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Popular 1", "year": 2024},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "2",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = PopularShowsClient()
        result = await client.get_popular_shows(limit=1, page=1)

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert result.pagination.total_pages == 2


@pytest.mark.asyncio
async def test_favorited_shows_pagination():
    """Test favorited shows pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"user_count": 500, "show": {"title": "Favorited 1", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = ShowStatsClient()
        result = await client.get_favorited_shows(limit=1, period="weekly", page=1)

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        show_0 = result.data[0].get("show")
        assert show_0 is not None
        assert show_0["title"] == "Favorited 1"


@pytest.mark.asyncio
async def test_played_shows_pagination():
    """Test played shows pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "watcher_count": 1000,
            "play_count": 5000,
            "show": {"title": "Played 1", "year": 2024},
        },
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = ShowStatsClient()
        result = await client.get_played_shows(limit=1, period="weekly", page=1)

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1


@pytest.mark.asyncio
async def test_watched_shows_pagination():
    """Test watched shows pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watcher_count": 2000, "show": {"title": "Watched 1", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = ShowStatsClient()
        result = await client.get_watched_shows(limit=1, period="weekly", page=1)

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1


@pytest.mark.asyncio
async def test_single_page_result():
    """Test pagination with a single page of results."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watchers": 100, "show": {"title": "Only Show", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = TrendingShowsClient()
        result = await client.get_trending_shows(limit=10, page=1)

        assert isinstance(result, PaginatedResponse)
        assert result.is_single_page
        assert not result.pagination.has_next_page
        assert not result.pagination.has_previous_page


@pytest.mark.asyncio
async def test_empty_result():
    """Test pagination with empty results."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",  # Changed from "0" to "1" - minimum valid value
        "X-Pagination-Item-Count": "0",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # For auto-pagination (page=None), mock should return empty result on first call
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = TrendingShowsClient()
        result = await client.get_trending_shows(limit=10, page=None)

        # Auto-pagination with empty results should return empty list
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
async def test_multiple_pages_auto_paginate():
    """Test auto-pagination fetches all pages correctly."""
    # Create 3 pages of mock responses
    responses: list[MagicMock] = []
    for page_num in range(1, 4):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "watchers": 100 - (page_num - 1) * 10,
                "show": {"title": f"Show {page_num}", "year": 2024},
            }
        ]
        mock_response.headers = {
            "X-Pagination-Page": str(page_num),
            "X-Pagination-Limit": "1",
            "X-Pagination-Page-Count": "3",
            "X-Pagination-Item-Count": "3",
        }
        mock_response.raise_for_status = MagicMock()
        responses.append(mock_response)

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(side_effect=responses)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = TrendingShowsClient()
        result = await client.get_trending_shows(limit=1, page=None)

        # Should fetch all 3 pages and return flat list
        assert isinstance(result, list)
        assert len(result) == 3
        show_0 = result[0].get("show")
        assert show_0 is not None
        assert show_0["title"] == "Show 1"
        show_1 = result[1].get("show")
        assert show_1 is not None
        assert show_1["title"] == "Show 2"
        show_2 = result[2].get("show")
        assert show_2 is not None
        assert show_2["title"] == "Show 3"
