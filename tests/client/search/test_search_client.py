import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.search import SearchClient


@pytest.mark.asyncio
async def test_search_shows():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "type": "show",
            "score": 100.0,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": "1", "slug": "breaking-bad"},
            },
        },
        {
            "type": "show",
            "score": 80.0,
            "show": {
                "title": "Better Call Saul",
                "year": 2015,
                "ids": {"trakt": "2", "slug": "better-call-saul"},
            },
        },
    ]
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
        result = await client.search_shows("Breaking Bad", limit=10)

        assert len(result) == 2
        assert result[0]["type"] == "show"
        assert result[0]["score"] == 100.0
        assert result[0].get("show", {}).get("title") == "Breaking Bad"
        assert result[1].get("show", {}).get("title") == "Better Call Saul"


@pytest.mark.asyncio
async def test_search_movies():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "type": "movie",
            "score": 95.0,
            "movie": {
                "title": "The Shawshank Redemption",
                "year": 1994,
                "ids": {"trakt": "1", "slug": "the-shawshank-redemption-1994"},
            },
        },
        {
            "type": "movie",
            "score": 90.0,
            "movie": {
                "title": "The Godfather",
                "year": 1972,
                "ids": {"trakt": "2", "slug": "the-godfather-1972"},
            },
        },
    ]
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
        result = await client.search_movies("Shawshank", limit=10)

        assert len(result) == 2
        assert result[0]["type"] == "movie"
        assert result[0]["score"] == 95.0
        assert result[0].get("movie", {}).get("title") == "The Shawshank Redemption"
        assert result[1].get("movie", {}).get("title") == "The Godfather"
