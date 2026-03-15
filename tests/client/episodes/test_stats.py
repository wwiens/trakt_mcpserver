import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.episodes import EpisodesClient


@pytest.mark.asyncio
async def test_get_episode_stats():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "watchers": 50000,
        "plays": 75000,
        "collectors": 30000,
        "comments": 150,
        "lists": 500,
        "votes": 12000,
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
        result = await client.get_episode_stats("game-of-thrones", 1, 1)

        assert result["watchers"] == 50000
        assert result["plays"] == 75000
        assert result["collectors"] == 30000

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert "/seasons/1/episodes/1/stats" in call_args[0][0]

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
