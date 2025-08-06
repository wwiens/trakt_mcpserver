"""Show tools for the Trakt MCP server."""

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.server.fastmcp import FastMCP

from client.shows.details import ShowDetailsClient
from client.shows.popular import PopularShowsClient
from client.shows.stats import ShowStatsClient
from client.shows.trending import TrendingShowsClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.shows import ShowFormatters
from server.base import BaseToolErrorMixin

if TYPE_CHECKING:
    from models.types import ShowResponse, TraktRating, TrendingWrapper
from utils.api.errors import MCPError

logger = logging.getLogger("trakt_mcp")


async def fetch_trending_shows(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch trending shows from Trakt.

    Args:
        limit: Maximum number of shows to return

    Returns:
        Information about trending shows
    """
    # Validate parameters first
    BaseToolErrorMixin.validate_required_params(limit=limit)

    try:
        client: TrendingShowsClient = TrendingShowsClient()
        shows: list[TrendingWrapper] = await client.get_trending_shows(limit=limit)
        return ShowFormatters.format_trending_shows(shows)

    except MCPError:
        raise
    except Exception as e:
        raise BaseToolErrorMixin.handle_unexpected_error(
            "fetch trending shows", e, limit=limit
        ) from e


async def fetch_popular_shows(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch popular shows from Trakt.

    Args:
        limit: Maximum number of shows to return

    Returns:
        Information about popular shows
    """
    # Validate parameters first
    BaseToolErrorMixin.validate_required_params(limit=limit)

    try:
        client: PopularShowsClient = PopularShowsClient()
        shows: list[ShowResponse] = await client.get_popular_shows(limit=limit)
        return ShowFormatters.format_popular_shows(shows)

    except MCPError:
        raise
    except Exception as e:
        raise BaseToolErrorMixin.handle_unexpected_error(
            "fetch popular shows", e, limit=limit
        ) from e


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
    client: ShowStatsClient = ShowStatsClient()
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
    client: ShowStatsClient = ShowStatsClient()
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
    client: ShowStatsClient = ShowStatsClient()
    shows = await client.get_watched_shows(limit=limit, period=period)
    return ShowFormatters.format_watched_shows(shows)


async def fetch_show_ratings(show_id: str) -> str:
    """Fetch ratings for a show from Trakt.

    Args:
        show_id: Trakt ID of the show

    Returns:
        Information about show ratings including average and distribution

    Raises:
        InvalidParamsError: If show_id is invalid
        InternalError: If an error occurs fetching show or ratings data
    """
    # Validate required parameters
    BaseToolErrorMixin.validate_required_params(show_id=show_id)

    client: ShowDetailsClient = ShowDetailsClient()

    try:
        show_data: ShowResponse = await client.get_show(show_id)

        # Handle transitional case where API returns error strings
        if isinstance(show_data, str):
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type="show",
                resource_id=show_id,
                error_message=show_data,
                operation="fetch_show_details",
            )

        show: ShowResponse = show_data
        show_title = show.get("title", "Unknown Show")
        ratings: TraktRating = await client.get_show_ratings(show_id)

        # Handle transitional case where API returns error strings
        if isinstance(ratings, str):
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type="show_ratings",
                resource_id=show_id,
                error_message=ratings,
                operation="fetch_show_ratings",
                show_title=show_title,
            )

        return ShowFormatters.format_show_ratings(ratings, show_title)
    except MCPError:
        raise
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="fetch show ratings", error=e, show_id=show_id
        ) from e


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

    Raises:
        InvalidParamsError: If show_id is invalid
        InternalError: If an error occurs fetching show data
    """
    # Validate required parameters
    BaseToolErrorMixin.validate_required_params(show_id=show_id)

    client: ShowDetailsClient = ShowDetailsClient()

    try:
        if extended:
            show_data: ShowResponse = await client.get_show_extended(show_id)
            # Handle transitional case where API returns error strings
            if isinstance(show_data, str):
                raise BaseToolErrorMixin.handle_api_string_error(
                    resource_type="show_extended",
                    resource_id=show_id,
                    error_message=show_data,
                    operation="fetch_show_extended",
                )
            return ShowFormatters.format_show_extended(show_data)
        else:
            show_data: ShowResponse = await client.get_show(show_id)
            # Handle transitional case where API returns error strings
            if isinstance(show_data, str):
                raise BaseToolErrorMixin.handle_api_string_error(
                    resource_type="show",
                    resource_id=show_id,
                    error_message=show_data,
                    operation="fetch_show_summary",
                )
            return ShowFormatters.format_show_summary(show_data)
    except MCPError:
        raise
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="fetch show summary", error=e, show_id=show_id, extended=extended
        ) from e


def register_show_tools(mcp: FastMCP) -> tuple[Any, Any, Any, Any, Any, Any, Any]:
    """Register show tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

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

    # Return handlers for type checker visibility
    return (
        fetch_trending_shows_tool,
        fetch_popular_shows_tool,
        fetch_favorited_shows_tool,
        fetch_played_shows_tool,
        fetch_watched_shows_tool,
        fetch_show_ratings_tool,
        fetch_show_summary_tool,
    )
