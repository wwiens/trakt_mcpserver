"""Tests for checkin tools."""

from unittest.mock import AsyncMock, patch

import pytest

from models.types.api_responses import CheckinResponse
from server.checkin.tools import checkin_to_show
from utils.api.error_types import (
    AuthenticationRequiredError,
    InvalidParamsError,
)


@pytest.fixture
def sample_checkin_response() -> CheckinResponse:
    """Sample checkin response for tests."""
    return {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "sharing": {"twitter": False, "mastodon": False, "tumblr": False},
        "show": {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": 1, "slug": "breaking-bad"},
        },
        "episode": {
            "season": 1,
            "number": 1,
            "title": "Pilot",
            "ids": {"trakt": 73640, "slug": "pilot"},
        },
    }


@pytest.mark.asyncio
async def test_checkin_to_show_authenticated(
    sample_checkin_response: CheckinResponse,
) -> None:
    """Test checking in to a show when authenticated."""

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        mock_client.checkin_to_show = AsyncMock(return_value=sample_checkin_response)

        # Call the tool function
        result = await checkin_to_show(season=1, episode=1, show_id="1")

        # Verify the result
        assert "# Successfully Checked In" in result
        assert "Breaking Bad" in result
        assert "S01E01" in result

        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
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
async def test_checkin_to_show_not_authenticated() -> None:
    """Test checking in to a show when not authenticated."""
    with (
        patch("server.checkin.tools.CheckinClient") as mock_client_class,
    ):
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        # Call the tool function - should raise AuthenticationRequiredError
        with pytest.raises(AuthenticationRequiredError) as exc_info:
            await checkin_to_show(season=1, episode=1, show_id="1")

        # Verify error contains expected information
        assert exc_info.value.data is not None
        assert exc_info.value.data["error_type"] == "auth_required"
        assert exc_info.value.data.get("auth_url")
        assert exc_info.value.data["action"]
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.checkin_to_show.assert_not_called()


@pytest.mark.asyncio
async def test_checkin_to_show_missing_info() -> None:
    """Test checking in to a show with missing information."""
    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        # Call the tool function with missing show_id and show_title - should raise error
        with pytest.raises(InvalidParamsError) as exc_info:
            await checkin_to_show(season=1, episode=1)

        # Assert on structured fields instead of message substrings
        assert exc_info.value.code == -32602  # INVALID_PARAMS
        assert "Must provide one of" in str(exc_info.value)  # Fallback check

        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.checkin_to_show.assert_not_called()


@pytest.mark.asyncio
async def test_checkin_to_show_with_title(
    sample_checkin_response: CheckinResponse,
) -> None:
    """Test checking in to a show using title instead of ID."""

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        mock_client.checkin_to_show = AsyncMock(return_value=sample_checkin_response)

        result = await checkin_to_show(
            season=1, episode=1, show_title="Breaking Bad", show_year=2008
        )

        assert "# Successfully Checked In" in result
        assert "Breaking Bad" in result

        mock_client.is_authenticated.assert_called_once()
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
async def test_checkin_to_show_with_all_parameters(
    sample_checkin_response: CheckinResponse,
) -> None:
    """Test checking in to a show with all parameters provided."""
    # Customize response for this test (S02E05)
    custom_response = sample_checkin_response.copy()
    custom_response["episode"] = {
        "season": 2,
        "number": 5,
        "title": "Breakage",
        "ids": {"trakt": 73645, "slug": "breakage"},
    }

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        mock_client.checkin_to_show = AsyncMock(return_value=custom_response)

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
async def test_checkin_to_show_title_only(
    sample_checkin_response: CheckinResponse,
) -> None:
    """Test checking in to a show with only title (no year)."""
    # Customize response for Friends show
    custom_response = sample_checkin_response.copy()
    custom_response["show"] = {
        "title": "Friends",
        "year": 1994,
        "ids": {"trakt": 2, "slug": "friends"},
    }
    custom_response["episode"] = {
        "season": 1,
        "number": 1,
        "title": "The One Where Monica Gets a Roommate",
        "ids": {"trakt": 73641, "slug": "the-one-where-monica-gets-a-roommate"},
    }

    with patch("server.checkin.tools.CheckinClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        mock_client.checkin_to_show = AsyncMock(return_value=custom_response)

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
