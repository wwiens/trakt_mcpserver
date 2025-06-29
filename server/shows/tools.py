# pyright: reportUnusedFunction=none
"""Show tools for the Trakt MCP server."""

import json
import logging

from mcp.server.fastmcp import FastMCP

from client.shows import ShowsClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.shows import ShowFormatters

logger = logging.getLogger("trakt_mcp")


async def fetch_trending_shows(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch trending shows from Trakt.

    Args:
        limit: Maximum number of shows to return

    Returns:
        Information about trending shows
    """
    client = ShowsClient()
    shows = await client.get_trending_shows(limit=limit)
    return ShowFormatters.format_trending_shows(shows)


async def fetch_popular_shows(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch popular shows from Trakt.

    Args:
        limit: Maximum number of shows to return

    Returns:
        Information about popular shows
    """
    client = ShowsClient()
    shows = await client.get_popular_shows(limit=limit)
    return ShowFormatters.format_popular_shows(shows)


async def fetch_favorited_shows(
    limit: int = DEFAULT_LIMIT, period: str = "weekly"
) -> str:
    """Fetch most favorited shows from Trakt.

    Args:
        limit: Maximum number of shows to return
        period: Time period for favorite calculation (daily, weekly, monthly, yearly, all)

    Returns:
        Information about most favorited shows
    """
    client = ShowsClient()
    shows = await client.get_favorited_shows(limit=limit, period=period)

    # Log the first show to see the structure
    if shows and len(shows) > 0:
        logger.info(
            f"Favorited shows API response structure: {json.dumps(shows[0], indent=2)}"
        )

    return ShowFormatters.format_favorited_shows(shows)


async def fetch_played_shows(limit: int = DEFAULT_LIMIT, period: str = "weekly") -> str:
    """Fetch most played shows from Trakt.

    Args:
        limit: Maximum number of shows to return
        period: Time period for most played (daily, weekly, monthly, yearly, all)

    Returns:
        Information about most played shows
    """
    client = ShowsClient()
    shows = await client.get_played_shows(limit=limit, period=period)
    return ShowFormatters.format_played_shows(shows)


async def fetch_watched_shows(
    limit: int = DEFAULT_LIMIT, period: str = "weekly"
) -> str:
    """Fetch most watched shows from Trakt.

    Args:
        limit: Maximum number of shows to return
        period: Time period for most watched (daily, weekly, monthly, yearly, all)

    Returns:
        Information about most watched shows
    """
    client = ShowsClient()
    shows = await client.get_watched_shows(limit=limit, period=period)
    return ShowFormatters.format_watched_shows(shows)


async def fetch_show_ratings(show_id: str) -> str:
    """Fetch ratings for a show from Trakt.

    Args:
        show_id: Trakt ID of the show

    Returns:
        Information about show ratings including average and distribution
    """
    client = ShowsClient()

    try:
        show = await client.get_show(show_id)

        # Check if the API returned an error string
        if isinstance(show, str):
            return f"Error fetching show details: {show}"

        show_title = show.get("title", "Unknown Show")
        ratings = await client.get_show_ratings(show_id)

        # Check if the API returned an error string
        if isinstance(ratings, str):
            return f"Error fetching ratings for {show_title}: {ratings}"

        return ShowFormatters.format_show_ratings(ratings, show_title)
    except Exception as e:
        logger.error(f"Error fetching show ratings: {e}")
        return f"Error fetching ratings for show ID {show_id}: {e!s}"


def register_show_tools(mcp: FastMCP) -> None:
    """Register show tools with the MCP server."""

    @mcp.tool(name=TOOL_NAMES["fetch_trending_shows"])
    async def fetch_trending_shows_tool(limit: int = DEFAULT_LIMIT) -> str:
        return await fetch_trending_shows(limit)

    @mcp.tool(name=TOOL_NAMES["fetch_popular_shows"])
    async def fetch_popular_shows_tool(limit: int = DEFAULT_LIMIT) -> str:
        return await fetch_popular_shows(limit)

    @mcp.tool(name=TOOL_NAMES["fetch_favorited_shows"])
    async def fetch_favorited_shows_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_favorited_shows(limit, period)

    @mcp.tool(name=TOOL_NAMES["fetch_played_shows"])
    async def fetch_played_shows_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_played_shows(limit, period)

    @mcp.tool(name=TOOL_NAMES["fetch_watched_shows"])
    async def fetch_watched_shows_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_watched_shows(limit, period)

    @mcp.tool(name=TOOL_NAMES["fetch_show_ratings"])
    async def fetch_show_ratings_tool(show_id: str) -> str:
        return await fetch_show_ratings(show_id)
