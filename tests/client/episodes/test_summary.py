import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.episodes import EpisodesClient


@pytest.mark.asyncio
async def test_get_episode():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "season": 1,
        "number": 1,
        "title": "Winter Is Coming",
        "ids": {"trakt": 62085, "tvdb": 3254641, "imdb": "tt1480055", "tmdb": 62085},
        "overview": "Ned Stark is the lord of Winterfell.",
        "first_aired": "2011-04-17T07:00:00.000Z",
        "rating": 8.5,
        "votes": 1000,
        "runtime": 62,
        "comment_count": 50,
        "available_translations": ["en", "es", "de"],
    }
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

        client = EpisodesClient()
        result = await client.get_episode("game-of-thrones", 1, 1)

        assert result["season"] == 1
        assert result["number"] == 1
        assert result["title"] == "Winter Is Coming"
        assert result["runtime"] == 62

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert "/seasons/1/episodes/1" in call_args[0][0]
        assert call_args[1]["params"] == {"extended": "full"}

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
