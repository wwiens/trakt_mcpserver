import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.seasons import SeasonsClient


@pytest.mark.asyncio
async def test_get_season_people():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cast": [
            {
                "characters": ["Daenerys Targaryen"],
                "episode_count": 10,
                "person": {
                    "name": "Emilia Clarke",
                    "ids": {"trakt": 436521, "imdb": "nm3592338", "tmdb": 1223786},
                },
            },
            {
                "characters": ["Jon Snow"],
                "episode_count": 10,
                "person": {
                    "name": "Kit Harington",
                    "ids": {"trakt": 436522, "imdb": "nm3229685", "tmdb": 239019},
                },
            },
        ],
        "crew": {
            "directing": [
                {
                    "jobs": ["Director"],
                    "episode_count": 2,
                    "person": {
                        "name": "Tim Van Patten",
                        "ids": {"trakt": 12345, "imdb": "nm0887678", "tmdb": 58620},
                    },
                },
            ],
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

        client = SeasonsClient()
        result = await client.get_season_people("game-of-thrones", 1)

        assert len(result["cast"]) == 2
        assert result["cast"][0]["person"]["name"] == "Emilia Clarke"
        assert result["cast"][0]["characters"] == ["Daenerys Targaryen"]
        assert result["cast"][0]["episode_count"] == 10
        assert "directing" in result["crew"]

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert "/seasons/1/people" in call_args[0][0]

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
