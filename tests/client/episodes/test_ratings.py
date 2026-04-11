import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.episodes import EpisodesClient


@pytest.mark.asyncio
async def test_get_episode_ratings():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "rating": 8.57053,
        "votes": 1234,
        "distribution": {
            "1": 10,
            "2": 5,
            "3": 8,
            "4": 12,
            "5": 30,
            "6": 50,
            "7": 120,
            "8": 300,
            "9": 400,
            "10": 299,
        },
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
        result = await client.get_episode_ratings("game-of-thrones", 1, 1)
        assert not isinstance(result, str)

        assert result["rating"] == 8.57053
        assert result["votes"] == 1234
        assert result["distribution"]["10"] == 299

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert "/seasons/1/episodes/1/ratings" in call_args[0][0]

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
