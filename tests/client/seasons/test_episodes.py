import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.seasons import SeasonsClient


@pytest.mark.asyncio
async def test_get_season_episodes():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "season": 1,
            "number": 1,
            "title": "Winter Is Coming",
            "ids": {
                "trakt": 62085,
                "tvdb": 3254641,
                "imdb": "tt1480055",
                "tmdb": 62085,
            },
            "overview": "The first episode.",
            "rating": 8.5,
            "votes": 500,
            "runtime": 62,
        },
        {
            "season": 1,
            "number": 2,
            "title": "The Kingsroad",
            "ids": {
                "trakt": 62086,
                "tvdb": 3436411,
                "imdb": "tt1668746",
                "tmdb": 62086,
            },
            "overview": "The second episode.",
            "rating": 8.3,
            "votes": 450,
            "runtime": 56,
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

        client = SeasonsClient()
        result = await client.get_season_episodes("game-of-thrones", 1)

        assert len(result) == 2
        assert result[0]["title"] == "Winter Is Coming"
        assert result[0]["number"] == 1
        assert result[1]["title"] == "The Kingsroad"

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert "/seasons/1" in call_args[0][0]
        assert call_args[1]["params"] == {"extended": "full"}

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
