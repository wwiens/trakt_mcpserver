"""Tests for search client pagination functionality."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.search.client import SearchClient
from models.types.pagination import PaginatedResponse


@pytest.mark.asyncio
async def test_search_shows_no_page_returns_all():
    """Test that search shows with no page parameter auto-paginates all results."""
    # Mock first page response
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [
        {"show": {"title": "Breaking Bad", "year": 2008, "ids": {"trakt": 1}}},
        {"show": {"title": "Better Call Saul", "year": 2015, "ids": {"trakt": 2}}},
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
        {"show": {"title": "Breaking Point", "year": 2021, "ids": {"trakt": 3}}},
        {"show": {"title": "Breakthrough", "year": 2022, "ids": {"trakt": 4}}},
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

        client = SearchClient()
        result = await client.search_shows(query="breaking", limit=2, page=None)

        # Should return a plain list with all 4 shows
        assert isinstance(result, list)
        assert len(result) == 4
        show_0 = result[0].get("show")
        assert show_0 is not None
        assert show_0["title"] == "Breaking Bad"
        show_3 = result[3].get("show")
        assert show_3 is not None
        assert show_3["title"] == "Breakthrough"


@pytest.mark.asyncio
async def test_search_shows_with_page_returns_paginated():
    """Test that search shows with page parameter returns PaginatedResponse."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"show": {"title": "Breaking Bad", "year": 2008, "ids": {"trakt": 1}}},
        {"show": {"title": "Better Call Saul", "year": 2015, "ids": {"trakt": 2}}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
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

        client = SearchClient()
        result = await client.search_shows(query="breaking", limit=2, page=1)

        # Should return PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert result.pagination.current_page == 1
        assert result.pagination.total_pages == 3
        assert result.pagination.total_items == 6
        show_0 = result.data[0].get("show")
        assert show_0 is not None
        assert show_0["title"] == "Breaking Bad"


@pytest.mark.asyncio
async def test_search_movies_no_page_returns_all():
    """Test that search movies with no page parameter auto-paginates all results."""
    # Mock first page response
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = [
        {"movie": {"title": "Inception", "year": 2010, "ids": {"trakt": 10}}},
        {"movie": {"title": "Interstellar", "year": 2014, "ids": {"trakt": 11}}},
    ]
    mock_response_page1.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "3",
    }
    mock_response_page1.raise_for_status = MagicMock()

    # Mock second page response
    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = [
        {"movie": {"title": "Insidious", "year": 2010, "ids": {"trakt": 12}}},
    ]
    mock_response_page2.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "3",
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

        client = SearchClient()
        result = await client.search_movies(query="in", limit=2, page=None)

        # Should return a plain list with all 3 movies
        assert isinstance(result, list)
        assert len(result) == 3
        movie_0 = result[0].get("movie")
        assert movie_0 is not None
        assert movie_0["title"] == "Inception"
        movie_2 = result[2].get("movie")
        assert movie_2 is not None
        assert movie_2["title"] == "Insidious"


@pytest.mark.asyncio
async def test_search_movies_with_page_returns_paginated():
    """Test that search movies with page parameter returns PaginatedResponse."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"movie": {"title": "Inception", "year": 2010, "ids": {"trakt": 10}}},
        {"movie": {"title": "Interstellar", "year": 2014, "ids": {"trakt": 11}}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "5",
        "X-Pagination-Item-Count": "10",
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

        client = SearchClient()
        result = await client.search_movies(query="in", limit=2, page=2)

        # Should return PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert result.pagination.current_page == 2
        assert result.pagination.total_pages == 5
        assert result.pagination.total_items == 10
        movie_0 = result.data[0].get("movie")
        assert movie_0 is not None
        assert movie_0["title"] == "Inception"


@pytest.mark.asyncio
async def test_search_pagination_metadata():
    """Test that pagination metadata is correctly extracted and computed."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"show": {"title": "Show 1", "year": 2020, "ids": {"trakt": 1}}},
    ]
    mock_response.headers = {
        "X-Pagination-Page": "3",
        "X-Pagination-Limit": "1",
        "X-Pagination-Page-Count": "5",
        "X-Pagination-Item-Count": "5",
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

        client = SearchClient()
        result = await client.search_shows(query="show", limit=1, page=3)

        # Verify pagination metadata
        assert result.pagination.current_page == 3
        assert result.pagination.items_per_page == 1
        assert result.pagination.total_pages == 5
        assert result.pagination.total_items == 5

        # Verify navigation properties
        assert result.pagination.has_previous_page
        assert result.pagination.has_next_page
        assert result.pagination.previous_page == 2
        assert result.pagination.next_page == 4


@pytest.mark.asyncio
async def test_search_empty_results():
    """Test search with no results."""
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

        client = SearchClient()

        # Test with page parameter
        result_paginated = await client.search_shows(
            query="nonexistent", limit=10, page=1
        )
        assert isinstance(result_paginated, PaginatedResponse)
        assert len(result_paginated.data) == 0
        assert result_paginated.pagination.total_items == 0

        # Reset mock for next test
        mock_instance.get.return_value = mock_response

        # Test without page parameter (auto-paginate)
        result_list = await client.search_movies(
            query="nonexistent", limit=10, page=None
        )
        assert isinstance(result_list, list)
        assert len(result_list) == 0
