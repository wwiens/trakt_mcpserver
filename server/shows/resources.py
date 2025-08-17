"""Show resources for the Trakt MCP server."""

import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.types import ShowResponse

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from client.shows.details import ShowDetailsClient
from client.shows.popular import PopularShowsClient
from client.shows.stats import ShowStatsClient
from client.shows.trending import TrendingShowsClient
from config.api import DEFAULT_LIMIT
from config.mcp.resources import MCP_RESOURCES
from models.formatters.shows import ShowFormatters
from server.base import BaseToolErrorMixin
from server.shows.tools import ShowIdParam
from utils.api.error_types import TraktValidationError
from utils.api.errors import handle_api_errors_func

logger: logging.Logger = logging.getLogger("trakt_mcp")

# Type alias for resource handler functions
type ResourceHandler = Callable[[], Awaitable[str]]


@handle_api_errors_func
async def get_trending_shows() -> str:
    """Returns the most watched shows over the last 24 hours from Trakt.

    Shows with the most watchers are returned first.

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

    # Debug log for API response structure analysis
    if shows:
        logger.debug(
            "Favorited shows API response structure",
            extra={
                "first_show_keys": list(shows[0].keys()),
                "show_count": len(shows),
                "first_show_type": type(shows[0]).__name__,
            },
        )

    return ShowFormatters.format_favorited_shows(shows)


@handle_api_errors_func
async def get_played_shows() -> str:
    """Returns the most played shows from Trakt in the specified time period.

    A single user can watch multiple episodes multiple times. Defaults to weekly.
    All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most played shows
    """
    client: ShowStatsClient = ShowStatsClient()
    shows = await client.get_played_shows(limit=DEFAULT_LIMIT)
    return ShowFormatters.format_played_shows(shows)


@handle_api_errors_func
async def get_watched_shows() -> str:
    """Returns the most watched (unique users) shows from Trakt.

    Data is from the specified time period, defaulting to weekly.
    All stats are relative to the specific time period.

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
    client: ShowDetailsClient = ShowDetailsClient()

    # Validate parameters with Pydantic for normalization and constraints
    try:
        params = ShowIdParam(show_id=show_id)
        show_id = params.show_id
    except ValidationError as e:
        error_details = {str(error["loc"][-1]): error["msg"] for error in e.errors()}
        raise TraktValidationError(
            f"Invalid parameters for show ratings: {', '.join(error_details.keys())}",
            invalid_params=list(error_details.keys()),
            validation_details=error_details,
        ) from e

    show = await client.get_show(show_id)

    # Handle transitional case where API returns error strings
    if isinstance(show, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="show",
            resource_id=show_id,
            error_message=show,
            operation="fetch_show_details",
        )

    # Type narrowing: show is guaranteed to be ShowResponse after string check
    show_data: ShowResponse = show
    show_title = show_data["title"]
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


def register_show_resources(
    mcp: FastMCP,
) -> tuple[
    ResourceHandler, ResourceHandler, ResourceHandler, ResourceHandler, ResourceHandler
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
