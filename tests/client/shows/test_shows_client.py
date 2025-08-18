import os
from unittest.mock import MagicMock, patch

import pytest

from client.shows import ShowsClient


@pytest.mark.asyncio
async def test_shows_client_get_trending_shows():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "watchers": 100,
            "show": {"title": "Breaking Bad", "year": 2008, "ids": {"trakt": "1"}},
        }
    ]
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = ShowsClient()
        result = await client.get_trending_shows(limit=1)

        assert len(result) == 1
        assert result[0]["watchers"] == 100
        assert result[0].get("show", {}).get("title") == "Breaking Bad"


@pytest.mark.asyncio
async def test_get_show_ratings():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "rating": 9.0,
        "votes": 1000,
        "distribution": {
            "10": 500,
            "9": 300,
            "8": 100,
            "7": 50,
            "6": 25,
            "5": 15,
            "4": 5,
            "3": 3,
            "2": 1,
            "1": 1,
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
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = ShowsClient()
        result = await client.get_show_ratings("1")

        assert isinstance(result, dict)
        assert result["rating"] == 9.0
        assert result["votes"] == 1000
        assert "distribution" in result


@pytest.mark.asyncio
async def test_get_show_extended():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "title": "Game of Thrones",
        "year": 2011,
        "ids": {
            "trakt": 1,
            "slug": "game-of-thrones",
            "tvdb": 121361,
            "imdb": "tt0944947",
            "tmdb": 1399,
        },
        "tagline": "Winter Is Coming",
        "overview": "Game of Thrones is an American fantasy drama television series created for HBO by David Benioff and D. B. Weiss. It is an adaptation of A Song of Ice and Fire, George R. R. Martin's series of fantasy novels, the first of which is titled A Game of Thrones.",
        "first_aired": "2011-04-18T01:00:00.000Z",
        "airs": {"day": "Sunday", "time": "21:00", "timezone": "America/New_York"},
        "runtime": 60,
        "certification": "TV-MA",
        "network": "HBO",
        "country": "us",
        "updated_at": "2014-08-22T08:32:06.000Z",
        "trailer": None,
        "homepage": "http://www.hbo.com/game-of-thrones/index.html",
        "status": "returning series",
        "rating": 9,
        "votes": 111,
        "comment_count": 92,
        "languages": ["en"],
        "available_translations": [
            "en",
            "tr",
            "sk",
            "de",
            "ru",
            "fr",
            "hu",
            "zh",
            "el",
            "pt",
            "es",
        ],
        "genres": ["drama", "fantasy"],
        "aired_episodes": 50,
        "original_title": "Game of Thrones",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = ShowsClient()
        result = await client.get_show_extended("1")

        # Verify the request was made with extended parameter
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args
        assert call_args[1]["params"] == {"extended": "full"}

        # Verify response data
        assert isinstance(result, dict)
        assert result["title"] == "Game of Thrones"
        assert result["year"] == 2011

        # Type-safe access to optional fields
        assert "status" in result
        assert result["status"] == "returning series"

        assert "certification" in result
        assert result["certification"] == "TV-MA"

        assert "network" in result
        assert result["network"] == "HBO"

        assert "runtime" in result
        assert result["runtime"] == 60

        assert "country" in result
        assert result["country"] == "us"

        assert "homepage" in result
        assert result["homepage"] == "http://www.hbo.com/game-of-thrones/index.html"

        assert "overview" in result
        assert "first_aired" in result
        assert "genres" in result
        assert "airs" in result
        assert result["airs"]["day"] == "Sunday"
        assert result["airs"]["time"] == "21:00"
        assert result["airs"]["timezone"] == "America/New_York"
