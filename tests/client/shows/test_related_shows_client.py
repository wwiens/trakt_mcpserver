"""Tests for related shows client module."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.shows.related import RelatedShowsClient


@pytest.mark.asyncio
async def test_get_related_shows_auto_pagination():
    """Test get_related_shows with auto-pagination mode (page=None)."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "Better Call Saul",
            "year": 2015,
            "overview": "A prequel to Breaking Bad.",
            "ids": {"trakt": 59660, "slug": "better-call-saul"},
        },
        {
            "title": "The Wire",
            "year": 2002,
            "overview": "A crime drama set in Baltimore.",
            "ids": {"trakt": 1234, "slug": "the-wire"},
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

        client = RelatedShowsClient()
        result = await client.get_related_shows("breaking-bad", limit=10)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "Better Call Saul"
        assert result[1]["title"] == "The Wire"

        mock_response.raise_for_status.assert_called()
        mock_instance.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_related_shows_single_page():
    """Test get_related_shows with single-page mode (page=N)."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "Better Call Saul",
            "year": 2015,
            "ids": {"trakt": 59660, "slug": "better-call-saul"},
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

        client = RelatedShowsClient()
        result = await client.get_related_shows("breaking-bad", limit=10, page=2)

        # Single-page mode returns PaginatedResponse with pagination metadata
        assert hasattr(result, "data")
        assert hasattr(result, "pagination")
        assert result.pagination.current_page == 2
        assert len(result.data) == 1
        assert result.data[0]["title"] == "Better Call Saul"

        mock_response.raise_for_status.assert_called()
        mock_instance.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_related_shows_url_encoding():
    """Test that show_id with special characters is URL encoded."""
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

        client = RelatedShowsClient()
        # Test with IMDB ID format
        await client.get_related_shows("tt0903747", limit=5)

        # Verify the request was made
        mock_instance.get.assert_called()
        call_args = mock_instance.get.call_args
        # The endpoint should contain the encoded show_id
        assert "tt0903747" in str(call_args)

        mock_instance.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_related_shows_empty_results():
    """Test get_related_shows with no related shows found."""
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

        client = RelatedShowsClient()
        result = await client.get_related_shows("obscure-show", limit=10)

        assert isinstance(result, list)
        assert len(result) == 0

        mock_instance.aclose.assert_awaited_once()
