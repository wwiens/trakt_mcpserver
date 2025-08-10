"""Show resources for the Trakt MCP server."""

import json
import logging
from collections.abc import Awaitable, Callable

from mcp.server.fastmcp import FastMCP

from client.shows.details import ShowDetailsClient
from client.shows.popular import PopularShowsClient
from client.shows.stats import ShowStatsClient
from client.shows.trending import TrendingShowsClient
from config.api import DEFAULT_LIMIT
from config.mcp.resources import MCP_RESOURCES
from models.formatters.shows import ShowFormatters
from server.base import BaseToolErrorMixin
from utils.api.errors import handle_api_errors_func

logger = logging.getLogger("trakt_mcp")


@handle_api_errors_func
async def get_trending_shows() -> str:
    """Returns the most watched shows over the last 24 hours from Trakt. Shows with the most watchers are returned first.

    Returns:
        Formatted markdown text with trending shows
    """
    client: TrendingShowsClient = TrendingShowsClient()
    shows = await client.get_trending_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_trending_shows(shows)


@handle_api_errors_func
async def get_popular_shows() -> str:
    """Returns the most popular shows from Trakt. Popularity is calculated using the rating percentage and the number of ratings.

    Returns:
        Formatted markdown text with popular shows
    """
    client: PopularShowsClient = PopularShowsClient()
    shows = await client.get_popular_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_popular_shows(shows)


@handle_api_errors_func
async def get_favorited_shows() -> str:
    """Returns the most favorited shows from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most favorited shows
    """
    client: ShowStatsClient = ShowStatsClient()
    shows = await client.get_favorited_shows(limit=DEFAULT_LIMIT)

    # Log the first show to see the structure
    if shows and len(shows) > 0:
        logger.info(
            f"Favorited shows API response structure: {json.dumps(shows[0], indent=2)}"
        )

    return ShowFormatters.format_favorited_shows(shows)


@handle_api_errors_func
async def get_played_shows() -> str:
    """Returns the most played (a single user can watch multiple episodes multiple times) shows from Traktin the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most played shows
    """
    client: ShowStatsClient = ShowStatsClient()
    shows = await client.get_played_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_played_shows(shows)


@handle_api_errors_func
async def get_watched_shows() -> str:
    """Returns the most watched (unique users) shows from Traktin the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most watched shows
    """
    client: ShowStatsClient = ShowStatsClient()
    shows = await client.get_watched_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_watched_shows(shows)


@handle_api_errors_func
async def get_show_ratings(show_id: str) -> str:
    """Returns ratings for a specific show from Trakt.

    Args:
        show_id: Trakt ID of the show

    Returns:
        Formatted markdown text with show ratings

    Raises:
        InvalidParamsError: If show_id is invalid
        InternalError: If an error occurs fetching show or ratings data
    """
    # Validate required parameters
    BaseToolErrorMixin.validate_required_params(show_id=show_id)
    client: ShowDetailsClient = ShowDetailsClient()

    try:
        show = await client.get_show(show_id)

        # Handle transitional case where API returns error strings
        if isinstance(show, str):
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type="show",
                resource_id=show_id,
                error_message=show,
                operation="fetch_show_details",
            )

        show_title = show.get("title", "Unknown Show")
        ratings = await client.get_show_ratings(show_id)

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
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="fetch show ratings", error=e, show_id=show_id
        ) from e


def register_show_resources(
    mcp: FastMCP,
) -> tuple[
    Callable[[], Awaitable[str]],
    Callable[[], Awaitable[str]],
    Callable[[], Awaitable[str]],
    Callable[[], Awaitable[str]],
    Callable[[], Awaitable[str]],
]:
    """Register show resources with the MCP server.

    Returns:
        Tuple of resource handlers for type checker visibility
    """

    @mcp.resource(
        uri=MCP_RESOURCES["shows_trending"],
        name="shows_trending",
        description="Most watched TV shows over the last 24 hours from Trakt",
        mime_type="text/markdown",
    )
    async def shows_trending_resource() -> str:
        return await get_trending_shows()

    @mcp.resource(
        uri=MCP_RESOURCES["shows_popular"],
        name="shows_popular",
        description="Most popular TV shows from Trakt based on ratings and votes",
        mime_type="text/markdown",
    )
    async def shows_popular_resource() -> str:
        return await get_popular_shows()

    @mcp.resource(
        uri=MCP_RESOURCES["shows_favorited"],
        name="shows_favorited",
        description="Most favorited TV shows from Trakt in the current weekly period",
        mime_type="text/markdown",
    )
    async def shows_favorited_resource() -> str:
        return await get_favorited_shows()

    @mcp.resource(
        uri=MCP_RESOURCES["shows_played"],
        name="shows_played",
        description="Most played TV shows from Trakt in the current weekly period",
        mime_type="text/markdown",
    )
    async def shows_played_resource() -> str:
        return await get_played_shows()

    @mcp.resource(
        uri=MCP_RESOURCES["shows_watched"],
        name="shows_watched",
        description="Most watched TV shows by unique users from Trakt in the current weekly period",
        mime_type="text/markdown",
    )
    async def shows_watched_resource() -> str:
        return await get_watched_shows()

    # Note: show_ratings moved to tools.py as @mcp.tool since it requires parameters

    # Return handlers for type checker visibility
    return (
        shows_trending_resource,
        shows_popular_resource,
        shows_favorited_resource,
        shows_played_resource,
        shows_watched_resource,
    )
