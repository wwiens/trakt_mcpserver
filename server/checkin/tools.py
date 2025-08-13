"""Checkin tools for the Trakt MCP server."""

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from client.checkin.client import CheckinClient
from config.mcp.tools import TOOL_NAMES
from models.formatters.checkin import CheckinFormatters
from server.base import BaseToolErrorMixin

# Import start_device_auth from auth module

logger = logging.getLogger("trakt_mcp")


async def checkin_to_show(
    season: int,
    episode: int,
    show_id: str | None = None,
    show_title: str | None = None,
    show_year: int | None = None,
    message: str = "",
    share_twitter: bool = False,
    share_mastodon: bool = False,
    share_tumblr: bool = False,
) -> str:
    """Check in to a show episode that the user is currently watching.

    This will mark the episode as watched on Trakt and can optionally share to connected social media.
    First use the search_shows tool to find the correct show_id before checking in, or provide the show title.

    Args:
        season: Season number
        episode: Episode number
        show_id: Trakt ID for the show (use search_shows to find this, optional if show_title is provided)
        show_title: Title of the show (optional if show_id is provided)
        show_year: Year the show was released (optional, can help with ambiguous titles)
        message: Optional message to include with the checkin
        share_twitter: Whether to share this checkin on Twitter
        share_mastodon: Whether to share this checkin on Mastodon
        share_tumblr: Whether to share this checkin on Tumblr

    Returns:
        Confirmation of the checkin

    Raises:
        AuthenticationRequiredError: If user is not authenticated
        InvalidParamsError: If required parameters are missing or invalid
        InternalError: If an unexpected error occurs
    """
    client = CheckinClient()

    # Check authentication
    if not client.is_authenticated():
        raise BaseToolErrorMixin.handle_authentication_required(
            action="check in to a show episode",
            show_id=show_id,
            show_title=show_title,
            season=season,
            episode=episode,
        )

    # Validate parameters
    BaseToolErrorMixin.validate_either_or_params(
        param_sets=[("show_id",), ("show_title",)],
        show_id=show_id,
        show_title=show_title,
    )

    try:
        # Attempt to check in to the show
        response = await client.checkin_to_show(
            episode_season=season,
            episode_number=episode,
            show_id=show_id,
            show_title=show_title,
            show_year=show_year,
            message=message,
            share_twitter=share_twitter,
            share_mastodon=share_mastodon,
            share_tumblr=share_tumblr,
        )

        # Format the response
        return CheckinFormatters.format_checkin_response(response)
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="check in to show episode",
            error=e,
            show_id=show_id,
            show_title=show_title,
            season=season,
            episode=episode,
            show_year=show_year,
        ) from e


def register_checkin_tools(mcp: FastMCP) -> Any:
    """Register checkin tools with the MCP server.

    Returns:
        Tool handler for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["checkin_to_show"],
        description="Check in to a TV show episode you're currently watching on Trakt",
    )
    async def checkin_to_show_tool(
        season: int,
        episode: int,
        show_id: str | None = None,
        show_title: str | None = None,
        show_year: int | None = None,
        message: str = "",
        share_twitter: bool = False,
        share_mastodon: bool = False,
        share_tumblr: bool = False,
    ) -> str:
        return await checkin_to_show(
            season,
            episode,
            show_id,
            show_title,
            show_year,
            message,
            share_twitter,
            share_mastodon,
            share_tumblr,
        )

    # Return handler for type checker visibility
    return checkin_to_show_tool
