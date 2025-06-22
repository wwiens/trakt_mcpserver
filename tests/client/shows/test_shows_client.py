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
        assert result[0]["show"]["title"] == "Breaking Bad"


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
