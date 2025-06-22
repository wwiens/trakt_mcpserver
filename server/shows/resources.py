# pyright: reportUnusedFunction=none
"""Show resources for the Trakt MCP server."""

import json
import logging

from mcp.server.fastmcp import FastMCP

from client.shows import ShowsClient
from config.api import DEFAULT_LIMIT
from config.mcp.resources import MCP_RESOURCES
from models.formatters.shows import ShowFormatters

logger = logging.getLogger("trakt_mcp")


async def get_trending_shows() -> str:
    """Returns the most watched shows over the last 24 hours from Trakt. Shows with the most watchers are returned first.

    Returns:
        Formatted markdown text with trending shows
    """
    client = ShowsClient()
    shows = await client.get_trending_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_trending_shows(shows)


async def get_popular_shows() -> str:
    """Returns the most popular shows from Trakt. Popularity is calculated using the rating percentage and the number of ratings.

    Returns:
        Formatted markdown text with popular shows
    """
    client = ShowsClient()
    shows = await client.get_popular_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_popular_shows(shows)


async def get_favorited_shows() -> str:
    """Returns the most favorited shows from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most favorited shows
    """
    client = ShowsClient()
    shows = await client.get_favorited_shows(limit=DEFAULT_LIMIT)

    # Log the first show to see the structure
    if shows and len(shows) > 0:
        logger.info(
            f"Favorited shows API response structure: {json.dumps(shows[0], indent=2)}"
        )

    return ShowFormatters.format_favorited_shows(shows)


async def get_played_shows() -> str:
    """Returns the most played (a single user can watch multiple episodes multiple times) shows from Traktin the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most played shows
    """
    client = ShowsClient()
    shows = await client.get_played_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_played_shows(shows)


async def get_watched_shows() -> str:
    """Returns the most watched (unique users) shows from Traktin the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most watched shows
    """
    client = ShowsClient()
    shows = await client.get_watched_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_watched_shows(shows)


async def get_show_ratings(show_id: str) -> str:
    """Returns ratings for a specific show from Trakt.

    Args:
        show_id: Trakt ID of the show

    Returns:
        Formatted markdown text with show ratings
    """
    client = ShowsClient()

    try:
        show = await client.get_show(show_id)

        # Check if the API returned an error string
        if isinstance(show, str):
            return f"Error fetching ratings for show ID {show_id}: {show}"

        show_title = show.get("title", "Unknown Show")
        ratings = await client.get_show_ratings(show_id)

        # Check if the API returned an error string
        if isinstance(ratings, str):
            return f"Error fetching ratings for {show_title}: {ratings}"

        return ShowFormatters.format_show_ratings(ratings, show_title)
    except Exception as e:
        logger.error(f"Error fetching show ratings: {e}")
        return f"Error fetching ratings for show ID {show_id}: {e!s}"


def register_show_resources(mcp: FastMCP) -> None:
    """Register show resources with the MCP server."""

    @mcp.resource(MCP_RESOURCES["shows_trending"])
    async def shows_trending_resource() -> str:
        return await get_trending_shows()

    @mcp.resource(MCP_RESOURCES["shows_popular"])
    async def shows_popular_resource() -> str:
        return await get_popular_shows()

    @mcp.resource(MCP_RESOURCES["shows_favorited"])
    async def shows_favorited_resource() -> str:
        return await get_favorited_shows()

    @mcp.resource(MCP_RESOURCES["shows_played"])
    async def shows_played_resource() -> str:
        return await get_played_shows()

    @mcp.resource(MCP_RESOURCES["shows_watched"])
    async def shows_watched_resource() -> str:
        return await get_watched_shows()

    # Note: show_ratings moved to tools.py as @mcp.tool since it requires parameters
