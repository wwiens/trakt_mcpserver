import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.episodes import EpisodesClient


@pytest.mark.asyncio
async def test_get_episode_videos():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "abc123",
            "url": "https://youtube.com/watch?v=abc123",
            "title": "Episode Preview",
            "type": "trailer",
            "language": "en",
        }
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

        client = EpisodesClient()
        result = await client.get_episode_videos("game-of-thrones", 1, 1)

        assert len(result) == 1
        assert result[0]["title"] == "Episode Preview"
        assert result[0]["type"] == "trailer"

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert "/seasons/1/episodes/1/videos" in call_args[0][0]

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
