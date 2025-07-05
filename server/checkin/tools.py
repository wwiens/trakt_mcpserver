# pyright: reportUnusedFunction=none
"""Checkin tools for the Trakt MCP server."""

import logging

from mcp.server.fastmcp import FastMCP

from client.checkin import CheckinClient
from config.mcp.tools import TOOL_NAMES
from models.formatters.checkin import CheckinFormatters

# Import start_device_auth from auth module
from ..auth.tools import start_device_auth

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
    """
    client = CheckinClient()

    if not client.is_authenticated():
        # Start the auth flow automatically
        auth_instructions = await start_device_auth()
        return f"""Authentication required to check in to a show.

{auth_instructions}

After you've completed the authorization process on the Trakt website, please tell me "I've completed the authorization" so I can check if it was successful and check you in to the show."""

    # Validate that either show_id or show_title is provided
    if not show_id and not show_title:
        return "Error: You must provide either a show_id or a show_title. Use the search_shows tool to find the correct show ID."

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
    except ValueError as e:
        # Handle authentication errors
        return f"Error: {e!s}"
    except Exception as e:
        # Handle other errors
        logger.error(f"Error checking in to show: {e}")
        return f"""An error occurred while checking in to the show: {e!s}

Make sure you provided either:
1. A valid show ID (use search_shows to find it)
   Example: `search_shows(query="Breaking Bad")`

OR

2. A show title (and optionally the year)
   Example: `checkin_to_show(show_title="Breaking Bad", show_year=2008, season=1, episode=1)`"""


def register_checkin_tools(mcp: FastMCP) -> None:
    """Register checkin tools with the MCP server."""

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
