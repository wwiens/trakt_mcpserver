# pyright: reportUnusedFunction=none
"""Show tools for the Trakt MCP server."""

from mcp.server.fastmcp import FastMCP

from client.shows import ShowsClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.shows import ShowFormatters


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
    show = await client.get_show(show_id)

    show_title = show.get("title", "Unknown Show")
    ratings = await client.get_show_ratings(show_id)

    return ShowFormatters.format_show_ratings(ratings, show_title)


async def fetch_show_summary(show_id: str, extended: bool = True) -> str:
    """Fetch show summary from Trakt.

    Args:
        show_id: Trakt ID of the show
        extended: If True, return comprehensive data with air times, production status and metadata.
                 If False, return basic show information (title, year, IDs).

    Returns:
        Show information formatted as markdown. Extended mode includes air times, production status,
        ratings, metadata, and detailed information. Basic mode includes title, year,
        and Trakt ID only.
    """
    client = ShowsClient()
    if extended:
        show = await client.get_show_extended(show_id)
        return ShowFormatters.format_show_extended(show)
    else:
        show = await client.get_show(show_id)
        return ShowFormatters.format_show_summary(show)


def register_show_tools(mcp: FastMCP) -> None:
    """Register show tools with the MCP server."""

    @mcp.tool(
        name=TOOL_NAMES["fetch_trending_shows"],
        description="Fetch trending TV shows from Trakt",
    )
    async def fetch_trending_shows_tool(limit: int = DEFAULT_LIMIT) -> str:
        return await fetch_trending_shows(limit)

    @mcp.tool(
        name=TOOL_NAMES["fetch_popular_shows"],
        description="Fetch popular TV shows from Trakt",
    )
    async def fetch_popular_shows_tool(limit: int = DEFAULT_LIMIT) -> str:
        return await fetch_popular_shows(limit)

    @mcp.tool(
        name=TOOL_NAMES["fetch_favorited_shows"],
        description="Fetch most favorited TV shows from Trakt",
    )
    async def fetch_favorited_shows_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_favorited_shows(limit, period)

    @mcp.tool(
        name=TOOL_NAMES["fetch_played_shows"],
        description="Fetch most played TV shows from Trakt",
    )
    async def fetch_played_shows_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_played_shows(limit, period)

    @mcp.tool(
        name=TOOL_NAMES["fetch_watched_shows"],
        description="Fetch most watched TV shows from Trakt",
    )
    async def fetch_watched_shows_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_watched_shows(limit, period)

    @mcp.tool(
        name=TOOL_NAMES["fetch_show_ratings"],
        description="Fetch ratings and voting statistics for a specific TV show",
    )
    async def fetch_show_ratings_tool(show_id: str) -> str:
        return await fetch_show_ratings(show_id)

    @mcp.tool(
        name=TOOL_NAMES["fetch_show_summary"],
        description="Get TV show summary from Trakt. Default behavior (extended=true): Returns comprehensive data including air times, production status, ratings, genres, runtime, network, and metadata. Basic mode (extended=false): Returns only title, year, and Trakt ID.",
    )
    async def fetch_show_summary_tool(show_id: str, extended: bool = True) -> str:
        return await fetch_show_summary(show_id, extended)
