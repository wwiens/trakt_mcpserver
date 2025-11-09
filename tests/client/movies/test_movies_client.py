import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.movies import MoviesClient


@pytest.mark.asyncio
async def test_get_movie_ratings():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "rating": 8.5,
        "votes": 2500,
        "distribution": {
            "10": 800,
            "9": 600,
            "8": 500,
            "7": 300,
            "6": 150,
            "5": 100,
            "4": 30,
            "3": 15,
            "2": 3,
            "1": 2,
        },
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

        client = MoviesClient()
        result = await client.get_movie_ratings("1")

        assert isinstance(result, dict)
        assert result["rating"] == 8.5
        assert result["votes"] == 2500
        assert "distribution" in result


@pytest.mark.asyncio
async def test_get_movie_extended():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "title": "TRON: Legacy",
        "year": 2010,
        "ids": {
            "trakt": 1,
            "slug": "tron-legacy-2010",
            "imdb": "tt1104001",
            "tmdb": 20526,
        },
        "tagline": "The Game Has Changed.",
        "overview": "Sam Flynn, the tech-savvy and daring son of Kevin Flynn, investigates his father's disappearance and is pulled into The Grid. With the help of a mysterious program named Quorra, Sam quests to stop evil dictator Clu from crossing into the real world.",
        "released": "2010-12-16",
        "runtime": 125,
        "country": "us",
        "updated_at": "2014-07-23T03:21:46.000Z",
        "trailer": None,
        "homepage": "http://disney.go.com/tron/",
        "status": "released",
        "rating": 8,
        "votes": 111,
        "comment_count": 92,
        "languages": ["en"],
        "available_translations": ["en"],
        "genres": ["action"],
        "certification": "PG-13",
        "original_title": "TRON: Legacy",
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

        client = MoviesClient()
        result = await client.get_movie_extended("1")

        # Verify the request was made with extended parameter
        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert call_args[1]["params"] == {"extended": "full"}

        # Verify response data
        assert isinstance(result, dict)
        assert result["title"] == "TRON: Legacy"
        assert result["year"] == 2010

        # Type-safe access to optional fields
        assert "status" in result
        assert result["status"] == "released"

        assert "tagline" in result
        assert result["tagline"] == "The Game Has Changed."

        assert "certification" in result
        assert result["certification"] == "PG-13"

        assert "runtime" in result
        assert result["runtime"] == 125

        assert "country" in result
        assert result["country"] == "us"

        assert "homepage" in result
        assert result["homepage"] == "http://disney.go.com/tron/"

        assert "overview" in result
        assert "released" in result
        assert "genres" in result
