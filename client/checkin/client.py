"""Check-in functionality for Trakt."""

from typing import Any

from config.endpoints import TRAKT_ENDPOINTS
from models.checkin import TraktCheckin
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


class CheckinClient(AuthClient):
    """Client for check-in operations."""

    @handle_api_errors
    async def checkin_to_show(
        self,
        episode_season: int,
        episode_number: int,
        show_id: str | None = None,
        show_title: str | None = None,
        show_year: int | None = None,
        message: str = "",
        share_twitter: bool = False,
        share_mastodon: bool = False,
        share_tumblr: bool = False,
    ) -> TraktCheckin:
        """Check in to a show episode the user is currently watching.

        Args:
            episode_season: Season number of the episode
            episode_number: Episode number within the season
            show_id: Trakt show ID (optional if show_title provided)
            show_title: Show title (optional if show_id provided)
            show_year: Show year (optional)
            message: Optional message for the check-in
            share_twitter: Whether to share on Twitter
            share_mastodon: Whether to share on Mastodon
            share_tumblr: Whether to share on Tumblr

        Returns:
            Check-in response data

        Raises:
            ValueError: If not authenticated or missing required parameters
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to check in to a show")

        if not show_id and not show_title:
            raise ValueError("Either show_id or show_title must be provided")

        # Prepare show data
        show_data: dict[str, Any] = (
            {"ids": {}} if not show_title else {"title": show_title}
        )

        # Add show ID if provided
        if show_id:
            if "ids" not in show_data:
                show_data["ids"] = {}
            show_data["ids"]["trakt"] = show_id

        # Add year if provided
        if show_year:
            show_data["year"] = show_year

        # Prepare episode data
        episode_data: dict[str, int] = {
            "season": episode_season,
            "number": episode_number,
        }

        # Prepare sharing data if any sharing options are enabled
        sharing_data: dict[str, bool] | None = None
        if share_twitter or share_mastodon or share_tumblr:
            sharing_data = {
                "twitter": share_twitter,
                "mastodon": share_mastodon,
                "tumblr": share_tumblr,
            }

        # Prepare checkin data
        data: dict[str, Any] = {"episode": episode_data, "show": show_data}

        # Add optional fields if provided
        if message:
            data["message"] = message

        if sharing_data:
            data["sharing"] = sharing_data

        # Make the checkin request
        response = await self._post_request(TRAKT_ENDPOINTS["checkin"], data)
        return TraktCheckin.from_api_response(response)
