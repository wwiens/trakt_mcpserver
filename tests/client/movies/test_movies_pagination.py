"""Tests for movie client pagination functionality."""

from unittest.mock import MagicMock

import pytest

from client.movies.popular import PopularMoviesClient
from client.movies.stats import MovieStatsClient
from client.movies.trending import TrendingMoviesClient
from models.types.pagination import PaginatedResponse
from utils.api.errors import InternalError


@pytest.mark.asyncio
async def test_trending_movies_no_page_returns_all(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that trending movies with no page parameter auto-paginates all results."""
    # Mock first page response
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [
        {"watchers": 100, "movie": {"title": "Movie 1", "year": 2024}},
        {"watchers": 90, "movie": {"title": "Movie 2", "year": 2024}},
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
        {"watchers": 80, "movie": {"title": "Movie 3", "year": 2024}},
        {"watchers": 70, "movie": {"title": "Movie 4", "year": 2024}},
    ]
    mock_response_page2.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "4",
    }
    mock_response_page2.raise_for_status = MagicMock()

    # Configure mock to return both pages
    patched_httpx_client.get.side_effect = [mock_response_page1, mock_response_page2]

    client = TrendingMoviesClient()
    result = await client.get_trending_movies(limit=2, page=None)

    # Should return a plain list with all 4 movies
    assert isinstance(result, list)
    assert len(result) == 4
    movie_0 = result[0].get("movie")
    assert movie_0 is not None
    assert movie_0["title"] == "Movie 1"
    movie_3 = result[3].get("movie")
    assert movie_3 is not None
    assert movie_3["title"] == "Movie 4"


@pytest.mark.asyncio
async def test_trending_movies_with_page_returns_paginated(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that trending movies with page parameter returns PaginatedResponse."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watchers": 100, "movie": {"title": "Movie 1", "year": 2024}},
        {"watchers": 90, "movie": {"title": "Movie 2", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "4",
    }
    mock_response.raise_for_status = MagicMock()

    patched_httpx_client.get.return_value = mock_response

    client = TrendingMoviesClient()
    result = await client.get_trending_movies(limit=2, page=1)

    # Should return PaginatedResponse
    assert isinstance(result, PaginatedResponse)
    assert len(result.data) == 2
    assert result.pagination.current_page == 1
    assert result.pagination.total_pages == 2
    assert result.pagination.total_items == 4


@pytest.mark.asyncio
async def test_trending_movies_pagination_metadata(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that pagination metadata is correctly parsed and exposed."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watchers": 80, "movie": {"title": "Movie 3", "year": 2024}},
        {"watchers": 70, "movie": {"title": "Movie 4", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "6",
    }
    mock_response.raise_for_status = MagicMock()

    patched_httpx_client.get.return_value = mock_response

    client = TrendingMoviesClient()
    result = await client.get_trending_movies(limit=2, page=2)

    # Check metadata properties
    assert result.pagination.current_page == 2
    assert result.pagination.items_per_page == 2
    assert result.pagination.total_pages == 3
    assert result.pagination.total_items == 6


@pytest.mark.asyncio
async def test_trending_movies_navigation_properties(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that navigation properties work correctly."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watchers": 80, "movie": {"title": "Movie 3", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "3",
    }
    mock_response.raise_for_status = MagicMock()

    patched_httpx_client.get.return_value = mock_response

    client = TrendingMoviesClient()
    result = await client.get_trending_movies(limit=1, page=2)

    # Check navigation properties
    assert result.pagination.has_previous_page
    assert result.pagination.has_next_page
    assert result.pagination.previous_page() == 1
    assert result.pagination.next_page() == 3


@pytest.mark.asyncio
async def test_popular_movies_no_page_returns_all(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that popular movies with no page parameter auto-paginates."""
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

    patched_httpx_client.get.return_value = mock_response

    client = PopularMoviesClient()
    result = await client.get_popular_movies(limit=2, page=None)

    # Should return a plain list
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["title"] == "Popular 1"


@pytest.mark.asyncio
async def test_popular_movies_with_page_returns_paginated(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that popular movies with page parameter returns PaginatedResponse."""
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

    patched_httpx_client.get.return_value = mock_response

    client = PopularMoviesClient()
    result = await client.get_popular_movies(limit=1, page=1)

    assert isinstance(result, PaginatedResponse)
    assert len(result.data) == 1
    assert result.pagination.total_pages == 2


@pytest.mark.asyncio
async def test_favorited_movies_no_page_returns_all(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that favorited movies with no page parameter auto-paginates."""
    # Mock two pages of responses
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [
        {"user_count": 500, "movie": {"title": "Favorited 1", "year": 2024}},
        {"user_count": 450, "movie": {"title": "Favorited 2", "year": 2024}},
    ]
    mock_response_page1.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "3",
    }
    mock_response_page1.raise_for_status = MagicMock()

    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = [
        {"user_count": 400, "movie": {"title": "Favorited 3", "year": 2024}},
    ]
    mock_response_page2.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "3",
    }
    mock_response_page2.raise_for_status = MagicMock()

    patched_httpx_client.get.side_effect = [mock_response_page1, mock_response_page2]

    client = MovieStatsClient()
    result = await client.get_favorited_movies(limit=2, period="weekly", page=None)

    # Should return a plain list with all 3 movies
    assert isinstance(result, list)
    assert len(result) == 3
    movie_0 = result[0].get("movie")
    assert movie_0 is not None
    assert movie_0["title"] == "Favorited 1"
    movie_2 = result[2].get("movie")
    assert movie_2 is not None
    assert movie_2["title"] == "Favorited 3"


@pytest.mark.asyncio
async def test_favorited_movies_pagination(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test favorited movies pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"user_count": 500, "movie": {"title": "Favorited 1", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    patched_httpx_client.get.return_value = mock_response

    client = MovieStatsClient()
    result = await client.get_favorited_movies(limit=1, period="weekly", page=1)

    assert isinstance(result, PaginatedResponse)
    assert len(result.data) == 1
    movie_0 = result.data[0].get("movie")
    assert movie_0 is not None
    assert movie_0["title"] == "Favorited 1"


@pytest.mark.asyncio
async def test_played_movies_no_page_returns_all(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that played movies with no page parameter auto-paginates."""
    # Mock two pages of responses
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [
        {
            "watcher_count": 1000,
            "play_count": 5000,
            "movie": {"title": "Played 1", "year": 2024},
        },
        {
            "watcher_count": 900,
            "play_count": 4500,
            "movie": {"title": "Played 2", "year": 2024},
        },
    ]
    mock_response_page1.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "3",
    }
    mock_response_page1.raise_for_status = MagicMock()

    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = [
        {
            "watcher_count": 800,
            "play_count": 4000,
            "movie": {"title": "Played 3", "year": 2024},
        },
    ]
    mock_response_page2.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "3",
    }
    mock_response_page2.raise_for_status = MagicMock()

    patched_httpx_client.get.side_effect = [mock_response_page1, mock_response_page2]

    client = MovieStatsClient()
    result = await client.get_played_movies(limit=2, period="weekly", page=None)

    # Should return a plain list with all 3 movies
    assert isinstance(result, list)
    assert len(result) == 3
    movie_0 = result[0].get("movie")
    assert movie_0 is not None
    assert movie_0["title"] == "Played 1"
    movie_2 = result[2].get("movie")
    assert movie_2 is not None
    assert movie_2["title"] == "Played 3"


@pytest.mark.asyncio
async def test_played_movies_pagination(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test played movies pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "watcher_count": 1000,
            "play_count": 5000,
            "movie": {"title": "Played 1", "year": 2024},
        },
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    patched_httpx_client.get.return_value = mock_response

    client = MovieStatsClient()
    result = await client.get_played_movies(limit=1, period="weekly", page=1)

    assert isinstance(result, PaginatedResponse)
    assert len(result.data) == 1


@pytest.mark.asyncio
async def test_watched_movies_no_page_returns_all(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that watched movies with no page parameter auto-paginates."""
    # Mock two pages of responses
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [
        {"watcher_count": 2000, "movie": {"title": "Watched 1", "year": 2024}},
        {"watcher_count": 1900, "movie": {"title": "Watched 2", "year": 2024}},
    ]
    mock_response_page1.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "3",
    }
    mock_response_page1.raise_for_status = MagicMock()

    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = [
        {"watcher_count": 1800, "movie": {"title": "Watched 3", "year": 2024}},
    ]
    mock_response_page2.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "3",
    }
    mock_response_page2.raise_for_status = MagicMock()

    patched_httpx_client.get.side_effect = [mock_response_page1, mock_response_page2]

    client = MovieStatsClient()
    result = await client.get_watched_movies(limit=2, period="weekly", page=None)

    # Should return a plain list with all 3 movies
    assert isinstance(result, list)
    assert len(result) == 3
    movie_0 = result[0].get("movie")
    assert movie_0 is not None
    assert movie_0["title"] == "Watched 1"
    movie_2 = result[2].get("movie")
    assert movie_2 is not None
    assert movie_2["title"] == "Watched 3"


@pytest.mark.asyncio
async def test_watched_movies_pagination(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test watched movies pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watcher_count": 2000, "movie": {"title": "Watched 1", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    patched_httpx_client.get.return_value = mock_response

    client = MovieStatsClient()
    result = await client.get_watched_movies(limit=1, period="weekly", page=1)

    assert isinstance(result, PaginatedResponse)
    assert len(result.data) == 1


@pytest.mark.asyncio
async def test_single_page_result(trakt_env: None, patched_httpx_client: MagicMock):
    """Test pagination with a single page of results."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"watchers": 100, "movie": {"title": "Only Movie", "year": 2024}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    patched_httpx_client.get.return_value = mock_response

    client = TrendingMoviesClient()
    result = await client.get_trending_movies(limit=10, page=1)

    assert isinstance(result, PaginatedResponse)
    assert result.is_single_page
    assert not result.pagination.has_next_page
    assert not result.pagination.has_previous_page


@pytest.mark.asyncio
async def test_empty_result(trakt_env: None, patched_httpx_client: MagicMock):
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

    patched_httpx_client.get.return_value = mock_response

    client = TrendingMoviesClient()
    result = await client.get_trending_movies(limit=10, page=None)

    # Auto-pagination with empty results should return empty list
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_multiple_pages_auto_paginate(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test auto-pagination fetches all pages correctly."""
    # Create 3 pages of mock responses
    responses: list[MagicMock] = []
    for page_num in range(1, 4):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "watchers": 100 - (page_num - 1) * 10,
                "movie": {"title": f"Movie {page_num}", "year": 2024},
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

    patched_httpx_client.get.side_effect = responses

    client = TrendingMoviesClient()
    result = await client.get_trending_movies(limit=1, page=None)

    # Should fetch all 3 pages and return flat list
    assert isinstance(result, list)
    assert len(result) == 3
    movie_0 = result[0].get("movie")
    assert movie_0 is not None
    assert movie_0["title"] == "Movie 1"
    movie_1 = result[1].get("movie")
    assert movie_1 is not None
    assert movie_1["title"] == "Movie 2"
    movie_2 = result[2].get("movie")
    assert movie_2 is not None
    assert movie_2["title"] == "Movie 3"


@pytest.mark.asyncio
async def test_auto_pagination_max_pages_safety_cap(
    trakt_env: None, patched_httpx_client: MagicMock
):
    """Test that InternalError is raised when max_pages limit is hit during auto-pagination.

    The RuntimeError from auto_paginate is wrapped in InternalError by the error handler.
    """
    # Create 101 mock pages (more than DEFAULT_MAX_PAGES which is 100)
    responses: list[MagicMock] = []
    for page_num in range(1, 102):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "watchers": 1000 - page_num,
                "movie": {"title": f"Movie {page_num}", "year": 2024},
            }
        ]
        mock_response.headers = {
            "X-Pagination-Page": str(page_num),
            "X-Pagination-Limit": "1",
            "X-Pagination-Page-Count": "101",
            "X-Pagination-Item-Count": "101",
        }
        mock_response.raise_for_status = MagicMock()
        responses.append(mock_response)

    patched_httpx_client.get.side_effect = responses

    client = TrendingMoviesClient()

    # Should raise InternalError (wrapping RuntimeError) when hitting max_pages limit
    with pytest.raises(InternalError) as exc_info:
        await client.get_trending_movies(limit=1, page=None)

    # Verify error message contains expected text about pagination safety limit
    error_message = str(exc_info.value)
    assert "Pagination safety limit reached" in error_message
    assert "100 pages fetched" in error_message
