import os
import time
from unittest.mock import MagicMock, patch

import pytest

from client.checkin import CheckinClient
from models.auth import TraktAuthToken


@pytest.mark.asyncio
async def test_checkin_to_show():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 12345,
        "watched_at": "2023-06-20T20:00:00.000Z",
        "sharing": {"twitter": True, "tumblr": False},
        "show": {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": "1", "slug": "breaking-bad"},
        },
        "episode": {
            "season": 1,
            "number": 1,
            "title": "Pilot",
            "ids": {"trakt": "73640"},
        },
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        client = CheckinClient()
        # Set up authentication
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        result = await client.checkin_to_show(
            show_id="1",
            episode_season=1,
            episode_number=1,
            message="Watching the pilot!",
        )

        assert isinstance(result, dict)
        assert result["id"] == 12345  # id is int in CheckinResponse

        # Type-safe access to optional fields
        assert "show" in result
        assert result["show"]["title"] == "Breaking Bad"

        assert "episode" in result
        assert result["episode"]["title"] == "Pilot"


@pytest.mark.asyncio
async def test_checkin_to_show_with_title():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 67890,
        "watched_at": "2023-06-20T21:00:00.000Z",
        "sharing": {"twitter": False, "tumblr": False},
        "show": {
            "title": "The Wire",
            "year": 2002,
            "ids": {"trakt": "2", "slug": "the-wire"},
        },
        "episode": {
            "season": 1,
            "number": 2,
            "title": "The Detail",
            "ids": {"trakt": "73641"},
        },
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        client = CheckinClient()
        # Set up authentication
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        result = await client.checkin_to_show(
            show_title="The Wire", episode_season=1, episode_number=2
        )

        assert isinstance(result, dict)
        assert result["id"] == 67890  # id is int in CheckinResponse

        # Type-safe access to optional fields
        assert "show" in result
        assert result["show"]["title"] == "The Wire"

        assert "episode" in result
        assert result["episode"]["title"] == "The Detail"


@pytest.mark.asyncio
async def test_checkin_to_show_not_authenticated():
    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        client = CheckinClient()
        # No authentication set

        with pytest.raises(ValueError) as exc_info:
            await client.checkin_to_show(
                show_id="1", episode_season=1, episode_number=1
            )

        assert "You must be authenticated to check in to a show" in str(exc_info.value)


@pytest.mark.asyncio
async def test_checkin_to_show_missing_info():
    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        client = CheckinClient()
        # Set up authentication
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        # Missing both show_id and show_title
        with pytest.raises(ValueError) as exc_info:
            await client.checkin_to_show(episode_season=1, episode_number=1)

        assert "Either show_id or show_title must be provided" in str(exc_info.value)
