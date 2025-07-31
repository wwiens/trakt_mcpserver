"""Tests for checkin tools."""

import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.checkin.tools import checkin_to_show


@pytest.mark.asyncio
async def test_checkin_to_show_authenticated():
    """Test checking in to a show when authenticated."""
    sample_response = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "show": {"title": "Breaking Bad", "year": 2008},
        "episode": {"season": 1, "number": 1, "title": "Pilot"},
    }

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_response)
        mock_client.checkin_to_show.return_value = future

        # Call the tool function
        result = await checkin_to_show(season=1, episode=1, show_id="1")

        # Verify the result
        assert "# Successfully Checked In" in result
        assert "Breaking Bad" in result
        assert "S01E01" in result

        # Verify the client methods were called
        mock_client.checkin_to_show.assert_called_once_with(
            episode_season=1,
            episode_number=1,
            show_id="1",
            show_title=None,
            show_year=None,
            message="",
            share_twitter=False,
            share_mastodon=False,
            share_tumblr=False,
        )


@pytest.mark.asyncio
async def test_checkin_to_show_not_authenticated():
    """Test checking in to a show when not authenticated."""
    with (
        patch("server.checkin.tools.CheckinClient") as mock_client_class,
        patch("server.checkin.tools.start_device_auth") as mock_start_auth,
    ):
        # Configure the mock to raise InvalidParamsError when checkin_to_show is called
        mock_client = mock_client_class.return_value

        # Mock checkin_to_show to raise InvalidParamsError (not authenticated)
        from config.errors import AUTH_REQUIRED
        from utils.api.errors import InvalidParamsError
        mock_client.checkin_to_show.side_effect = InvalidParamsError(AUTH_REQUIRED)

        # Mock the start_device_auth function
        mock_start_auth.return_value = (
            "# Trakt Authentication Required\n\nPlease authenticate..."
        )

        # Call the tool function
        result = await checkin_to_show(season=1, episode=1, show_id="1")

        # Verify the result
        assert "Authentication required" in result
        assert "# Trakt Authentication Required" in result

        # Verify the client methods were called
        mock_client.checkin_to_show.assert_called_once()
        mock_start_auth.assert_called_once()


@pytest.mark.asyncio
async def test_checkin_to_show_missing_info():
    """Test checking in to a show with missing information."""
    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        # Call the tool function with missing show_id and show_title
        result = await checkin_to_show(season=1, episode=1)

        # Verify the result
        assert "Error: Missing required parameter: show_id or show_title" in result

        # Verify the client methods were not called due to parameter validation
        mock_client.checkin_to_show.assert_not_called()


@pytest.mark.asyncio
async def test_checkin_to_show_with_title():
    """Test checking in to a show using title instead of ID."""
    sample_response = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "show": {"title": "Breaking Bad", "year": 2008},
        "episode": {"season": 1, "number": 1, "title": "Pilot"},
    }

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_response)
        mock_client.checkin_to_show.return_value = future

        result = await checkin_to_show(
            season=1, episode=1, show_title="Breaking Bad", show_year=2008
        )

        assert "# Successfully Checked In" in result
        assert "Breaking Bad" in result

        mock_client.checkin_to_show.assert_called_once_with(
            episode_season=1,
            episode_number=1,
            show_id=None,
            show_title="Breaking Bad",
            show_year=2008,
            message="",
            share_twitter=False,
            share_mastodon=False,
            share_tumblr=False,
        )


@pytest.mark.asyncio
async def test_checkin_to_show_with_message_and_sharing():
    """Test checking in to a show with message and social sharing."""
    sample_response = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "show": {"title": "Breaking Bad", "year": 2008},
        "episode": {"season": 1, "number": 1, "title": "Pilot"},
    }

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_response)
        mock_client.checkin_to_show.return_value = future

        result = await checkin_to_show(
            season=1,
            episode=1,
            show_id="1",
            message="Great episode!",
            share_twitter=True,
            share_mastodon=True,
        )

        assert "# Successfully Checked In" in result

        mock_client.checkin_to_show.assert_called_once_with(
            episode_season=1,
            episode_number=1,
            show_id="1",
            show_title=None,
            show_year=None,
            message="Great episode!",
            share_twitter=True,
            share_mastodon=True,
            share_tumblr=False,
        )


@pytest.mark.asyncio
async def test_checkin_to_show_value_error():
    """Test checking in to a show with ValueError - should propagate exception."""
    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(ValueError("Authentication failed"))
        mock_client.checkin_to_show.return_value = future

        with pytest.raises(ValueError) as exc_info:
            await checkin_to_show(season=1, episode=1, show_id="1")

        assert "Authentication failed" in str(exc_info.value)

        mock_client.checkin_to_show.assert_called_once()


@pytest.mark.asyncio
async def test_checkin_to_show_general_error():
    """Test checking in to a show with general error - should propagate exception."""
    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("Network error"))
        mock_client.checkin_to_show.return_value = future

        with pytest.raises(Exception) as exc_info:
            await checkin_to_show(season=1, episode=1, show_id="1")

        assert "Network error" in str(exc_info.value)

        mock_client.checkin_to_show.assert_called_once()


@pytest.mark.asyncio
async def test_checkin_to_show_with_all_parameters():
    """Test checking in to a show with all parameters provided."""
    sample_response = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "show": {"title": "Breaking Bad", "year": 2008},
        "episode": {"season": 2, "number": 5, "title": "Breakage"},
    }

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_response)
        mock_client.checkin_to_show.return_value = future

        result = await checkin_to_show(
            season=2,
            episode=5,
            show_id="1",
            show_title="Breaking Bad",
            show_year=2008,
            message="Intense episode!",
            share_twitter=True,
            share_mastodon=True,
            share_tumblr=True,
        )

        assert "# Successfully Checked In" in result
        assert "Breaking Bad" in result
        assert "S02E05" in result

        mock_client.checkin_to_show.assert_called_once_with(
            episode_season=2,
            episode_number=5,
            show_id="1",
            show_title="Breaking Bad",
            show_year=2008,
            message="Intense episode!",
            share_twitter=True,
            share_mastodon=True,
            share_tumblr=True,
        )


@pytest.mark.asyncio
async def test_checkin_to_show_title_only():
    """Test checking in to a show with only title (no year)."""
    sample_response = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "show": {"title": "Friends", "year": 1994},
        "episode": {
            "season": 1,
            "number": 1,
            "title": "The One Where Monica Gets a Roommate",
        },
    }

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_response)
        mock_client.checkin_to_show.return_value = future

        result = await checkin_to_show(season=1, episode=1, show_title="Friends")

        assert "# Successfully Checked In" in result
        assert "Friends" in result

        mock_client.checkin_to_show.assert_called_once_with(
            episode_season=1,
            episode_number=1,
            show_id=None,
            show_title="Friends",
            show_year=None,
            message="",
            share_twitter=False,
            share_mastodon=False,
            share_tumblr=False,
        )
