import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.shows import ShowsClient


@pytest.mark.asyncio
async def test_get_seasons():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "number": 0,
            "ids": {"trakt": 1, "tvdb": 137481, "tmdb": 3627},
            "rating": 9.0,
            "votes": 111,
            "episode_count": 10,
            "aired_episodes": 10,
            "title": "Specials",
            "overview": None,
            "first_aired": "2010-12-06T02:00:00.000Z",
            "network": "HBO",
        },
        {
            "number": 1,
            "ids": {"trakt": 2, "tvdb": 364731, "tmdb": 3624},
            "rating": 9.0,
            "votes": 111,
            "episode_count": 10,
            "aired_episodes": 10,
            "title": "Season 1",
            "overview": "Season 1 overview.",
            "first_aired": "2011-04-09T02:00:00.000Z",
            "network": "HBO",
        },
        {
            "number": 2,
            "ids": {"trakt": 3, "tvdb": 473271, "tmdb": 3625},
            "rating": 9.0,
            "votes": 111,
            "episode_count": 10,
            "aired_episodes": 10,
            "title": "Season 2",
            "overview": "Season 2 overview.",
            "first_aired": "2012-04-02T02:00:00.000Z",
            "network": "HBO",
        },
    ]
    mock_response.raise_for_status = MagicMock()

    mock_instance = MagicMock(spec=httpx.AsyncClient)
    mock_instance.get = AsyncMock(return_value=mock_response)
    mock_instance.post = AsyncMock()
    mock_instance.aclose = AsyncMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value = mock_instance

        client = ShowsClient()
        result = await client.get_seasons("game-of-thrones")

        assert len(result) == 3
        assert result[0]["number"] == 0
        assert result[0]["title"] == "Specials"
        assert result[0]["episode_count"] == 10
        assert result[1]["number"] == 1
        assert result[1]["title"] == "Season 1"
        assert result[1]["aired_episodes"] == 10
        assert result[2]["number"] == 2

        # Verify extended=full was passed
        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert call_args[1]["params"] == {"extended": "full"}

        # Verify lifecycle assertions
        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
