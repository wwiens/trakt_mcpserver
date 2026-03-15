import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.seasons import SeasonsClient


@pytest.mark.asyncio
async def test_get_season():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "number": 1,
        "ids": {"trakt": 3950, "tvdb": 364731, "tmdb": 3624},
        "rating": 8.57053,
        "votes": 1234,
        "episode_count": 10,
        "aired_episodes": 10,
        "title": "Season 1",
        "overview": "The first season overview.",
        "first_aired": "2011-04-17T07:00:00.000Z",
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

        client = SeasonsClient()
        result = await client.get_season("game-of-thrones", 1)

        assert result["number"] == 1
        assert result["title"] == "Season 1"
        assert result["episode_count"] == 10
        assert result["rating"] == 8.57053

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert "/seasons/1/info" in call_args[0][0]
        assert call_args[1]["params"] == {"extended": "full"}

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
