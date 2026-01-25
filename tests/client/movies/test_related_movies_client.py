"""Tests for related movies client module."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.movies.related import RelatedMoviesClient
from utils.api.error_types import TraktResourceNotFoundError


@pytest.mark.asyncio
async def test_get_related_movies_auto_pagination():
    """Test get_related_movies with auto-pagination mode (page=None)."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "The Dark Knight Rises",
            "year": 2012,
            "overview": "Eight years after the Joker's reign of anarchy.",
            "ids": {"trakt": 28, "slug": "the-dark-knight-rises"},
        },
        {
            "title": "Batman Begins",
            "year": 2005,
            "overview": "A young Bruce Wayne travels to the Far East.",
            "ids": {"trakt": 155, "slug": "batman-begins"},
        },
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
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
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = RelatedMoviesClient()
        result = await client.get_related_movies("the-dark-knight", limit=10)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "The Dark Knight Rises"
        assert result[1]["title"] == "Batman Begins"

        mock_response.raise_for_status.assert_called()
        mock_instance.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_related_movies_single_page():
    """Test get_related_movies with single-page mode (page=N)."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "The Dark Knight Rises",
            "year": 2012,
            "ids": {"trakt": 28, "slug": "the-dark-knight-rises"},
        }
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "25",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = RelatedMoviesClient()
        result = await client.get_related_movies("the-dark-knight", limit=10, page=2)

        # Single-page mode returns PaginatedResponse with pagination metadata
        assert hasattr(result, "data")
        assert hasattr(result, "pagination")
        assert result.pagination.current_page == 2
        assert len(result.data) == 1
        assert result.data[0]["title"] == "The Dark Knight Rises"

        mock_response.raise_for_status.assert_called()
        mock_instance.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_related_movies_url_encoding():
    """Test that movie_id with special characters is URL encoded."""
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
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = RelatedMoviesClient()
        # Test with a slug containing special characters that need encoding
        # / -> %2F, : -> %3A, & -> %26
        await client.get_related_movies("movie/with:special&chars", limit=5)

        # Verify the request was made
        mock_instance.get.assert_called()
        call_args = mock_instance.get.call_args
        # The endpoint should contain the URL-encoded movie_id
        assert "movie%2Fwith%3Aspecial%26chars" in str(call_args)

        mock_instance.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_related_movies_empty_results():
    """Test get_related_movies with no related movies found."""
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
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = RelatedMoviesClient()
        result = await client.get_related_movies("obscure-movie", limit=10)

        assert isinstance(result, list)
        assert len(result) == 0

        mock_instance.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_related_movies_api_error():
    """Test get_related_movies handles API errors correctly."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found",
        request=MagicMock(),
        response=MagicMock(status_code=404),
    )

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
        pytest.raises(TraktResourceNotFoundError),
    ):
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.post = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = RelatedMoviesClient()
        await client.get_related_movies("nonexistent-movie", limit=10)
