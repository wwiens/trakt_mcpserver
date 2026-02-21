import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.seasons import SeasonsClient


@pytest.mark.asyncio
async def test_get_season_lists():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "name": "Best Seasons Ever",
            "description": "A curated list of the best TV seasons.",
            "privacy": "public",
            "type": "personal",
            "display_numbers": True,
            "allow_comments": True,
            "sort_by": "rank",
            "sort_how": "asc",
            "item_count": 50,
            "comment_count": 10,
            "likes": 100,
            "ids": {"trakt": 1, "slug": "best-seasons-ever"},
            "user": {
                "username": "sean",
                "private": False,
                "name": "Sean Rudford",
                "vip": True,
                "ids": {"slug": "sean"},
            },
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
        result = await client.get_season_lists("game-of-thrones", 1)

        assert len(result) == 1
        assert result[0]["name"] == "Best Seasons Ever"
        assert result[0]["item_count"] == 50
        assert result[0]["likes"] == 100
        assert result[0]["user"]["username"] == "sean"

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert "/seasons/1/lists" in call_args[0][0]

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
