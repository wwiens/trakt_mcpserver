"""Tests for recommendations client pagination functionality."""

import time
from unittest.mock import MagicMock

import pytest

from client.recommendations import RecommendationsClient
from models.auth import TraktAuthToken
from models.types.pagination import PaginatedResponse


@pytest.fixture
def mock_auth_token() -> TraktAuthToken:
    """Create a mock auth token for testing."""
    return TraktAuthToken(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )


@pytest.fixture
def authenticated_client(mock_auth_token: TraktAuthToken) -> RecommendationsClient:
    """Create an authenticated recommendations client for testing."""
    client = RecommendationsClient()
    client.auth_token = mock_auth_token
    return client


@pytest.mark.asyncio
async def test_movie_recommendations_no_page_respects_limit(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that movie recommendations with no page parameter respects limit."""
    # Use page count of 1 to prevent auto-pagination from fetching multiple pages
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Movie 1", "year": 2024, "ids": {"trakt": 1}},
        {"title": "Movie 2", "year": 2024, "ids": {"trakt": 2}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "1",  # Only 1 page to stop auto-pagination
        "X-Pagination-Item-Count": "2",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result = await authenticated_client.get_movie_recommendations(limit=2, page=None)

    # Should return a list (auto-paginate mode)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].title == "Movie 1"
    assert result[1].title == "Movie 2"


@pytest.mark.asyncio
async def test_movie_recommendations_with_page_returns_paginated(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that movie recommendations with page parameter returns PaginatedResponse."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Movie 1", "year": 2024, "ids": {"trakt": 1}},
        {"title": "Movie 2", "year": 2024, "ids": {"trakt": 2}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "4",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result = await authenticated_client.get_movie_recommendations(limit=2, page=1)

    # Should return PaginatedResponse
    assert isinstance(result, PaginatedResponse)
    assert len(result.data) == 2
    assert result.pagination.current_page == 1
    assert result.pagination.total_pages == 2
    assert result.pagination.total_items == 4


@pytest.mark.asyncio
async def test_show_recommendations_no_page_respects_limit(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that show recommendations with no page parameter respects limit."""
    # Use page count of 1 to prevent auto-pagination from fetching multiple pages
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Show 1", "year": 2024, "ids": {"trakt": 1}},
        {"title": "Show 2", "year": 2024, "ids": {"trakt": 2}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "1",  # Only 1 page to stop auto-pagination
        "X-Pagination-Item-Count": "2",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result = await authenticated_client.get_show_recommendations(limit=2, page=None)

    # Should return a list (auto-paginate mode)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].title == "Show 1"
    assert result[1].title == "Show 2"


@pytest.mark.asyncio
async def test_show_recommendations_with_page_returns_paginated(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that show recommendations with page parameter returns PaginatedResponse."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Show 1", "year": 2024, "ids": {"trakt": 1}},
        {"title": "Show 2", "year": 2024, "ids": {"trakt": 2}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "4",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result = await authenticated_client.get_show_recommendations(limit=2, page=1)

    # Should return PaginatedResponse
    assert isinstance(result, PaginatedResponse)
    assert len(result.data) == 2
    assert result.pagination.current_page == 1
    assert result.pagination.total_pages == 2
    assert result.pagination.total_items == 4


@pytest.mark.asyncio
async def test_movie_recommendations_pagination_metadata(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that pagination metadata is correctly parsed and exposed."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Movie 3", "year": 2024, "ids": {"trakt": 3}},
        {"title": "Movie 4", "year": 2024, "ids": {"trakt": 4}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "6",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result = await authenticated_client.get_movie_recommendations(limit=2, page=2)

    # Check metadata properties
    assert result.pagination.current_page == 2
    assert result.pagination.items_per_page == 2
    assert result.pagination.total_pages == 3
    assert result.pagination.total_items == 6


@pytest.mark.asyncio
async def test_recommendations_navigation_properties(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that navigation properties work correctly."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Movie 3", "year": 2024, "ids": {"trakt": 3}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "3",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result = await authenticated_client.get_movie_recommendations(limit=1, page=2)

    # Check navigation properties
    assert result.pagination.has_previous_page
    assert result.pagination.has_next_page
    assert result.pagination.previous_page() == 1
    assert result.pagination.next_page() == 3


@pytest.mark.asyncio
async def test_empty_recommendations_result(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test handling of empty recommendations."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "0",
        "X-Pagination-Item-Count": "0",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result = await authenticated_client.get_movie_recommendations(limit=10)

    # Should return empty list
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_recommendations_with_favorited_by(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test recommendations include favorited_by data."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "Popular Movie",
            "year": 2024,
            "ids": {"trakt": 1},
            "favorited_by": [
                {
                    "user": {
                        "username": "user1",
                        "private": False,
                        "name": "User One",
                        "vip": True,
                        "ids": {"slug": "user1"},
                    },
                    "notes": "Great movie!",
                },
            ],
        },
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result = await authenticated_client.get_movie_recommendations(limit=10)

    assert isinstance(result, list)
    assert len(result) == 1
    movie = result[0]
    assert movie.title == "Popular Movie"
    assert len(movie.favorited_by) == 1
    assert movie.favorited_by[0].user.username == "user1"
    assert movie.favorited_by[0].notes == "Great movie!"
