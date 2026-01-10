"""Checkin tools for the Trakt MCP server."""

import logging
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from client.checkin.client import CheckinClient
from config.mcp.descriptions import (
    EPISODE_DESCRIPTION,
    SEASON_DESCRIPTION,
    SHOW_ID_DESCRIPTION,
)
from config.mcp.tools import TOOL_NAMES
from models.formatters.checkin import CheckinFormatters
from server.base import BaseToolErrorMixin

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
        season: Annotated[int, Field(description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(description=EPISODE_DESCRIPTION)],
        show_id: Annotated[
            str | None,
            Field(
                description=f"{SHOW_ID_DESCRIPTION}. Provide either show_id OR show_title."
            ),
        ] = None,
        show_title: Annotated[
            str | None,
            Field(
                description="Title of the show (e.g., 'Breaking Bad'). Provide either show_title OR show_id."
            ),
        ] = None,
        show_year: Annotated[
            int | None,
            Field(
                description="Year the show first aired (e.g., 2008). Helps disambiguate shows with the same title."
            ),
        ] = None,
        message: Annotated[
            str,
            Field(
                description="Optional message to share on connected social networks. If not provided, uses the user's default watching message."
            ),
        ] = "",
        share_twitter: Annotated[
            bool,
            Field(
                description="Share this check-in on Twitter. Overrides user's default sharing setting."
            ),
        ] = False,
        share_mastodon: Annotated[
            bool,
            Field(
                description="Share this check-in on Mastodon. Overrides user's default sharing setting."
            ),
        ] = False,
        share_tumblr: Annotated[
            bool,
            Field(
                description="Share this check-in on Tumblr. Overrides user's default sharing setting."
            ),
        ] = False,
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
