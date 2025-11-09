"""Show tools for the Trakt MCP server."""

import json
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, PositiveInt, field_validator

from client.shows.client import ShowsClient
from client.shows.details import ShowDetailsClient
from client.shows.popular import PopularShowsClient
from client.shows.stats import ShowStatsClient
from client.shows.trending import TrendingShowsClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.shows import ShowFormatters
from models.formatters.videos import VideoFormatters
from server.base import BaseToolErrorMixin
from utils.api.errors import MCPError, handle_api_errors_func

if TYPE_CHECKING:
    from models.types import ShowResponse, TraktRating

logger = logging.getLogger("trakt_mcp")

# Type alias for tool handlers
ToolHandler = Callable[..., Awaitable[str]]


# Pydantic models for parameter validation
class LimitOnly(BaseModel):
    """Parameters for tools that only require a limit."""

    limit: PositiveInt = DEFAULT_LIMIT
    page: int | None = Field(
        default=None, ge=1, description="Page number for pagination (optional)"
    )


class PeriodParams(BaseModel):
    """Parameters for tools that accept limit and time period."""

    limit: PositiveInt = DEFAULT_LIMIT
    period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly"
    page: int | None = Field(
        default=None, ge=1, description="Page number for pagination (optional)"
    )


class ShowIdParam(BaseModel):
    """Parameters for tools that require a show ID."""

    show_id: str = Field(..., min_length=1, description="Non-empty Trakt show ID")

    @field_validator("show_id", mode="before")
    @classmethod
    def _strip_show_id(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


class ShowSummaryParams(ShowIdParam):
    """Parameters for show summary tools with extended option."""

    extended: bool = True


class ShowVideoParams(ShowIdParam):
    """Parameters for show video tools."""

    embed_markdown: bool = True


@handle_api_errors_func
async def fetch_trending_shows(
    limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Fetch trending shows from Trakt.

    Args:
        limit: Items per page (default: 10)
        page: Page number (optional). If None, returns all results via auto-pagination.

    Returns:
        Information about trending shows. When page is None, returns all shows.
        When page is specified, returns shows from that page with pagination metadata.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = LimitOnly(limit=limit, page=page)
    limit, page = params.limit, params.page

    client = TrendingShowsClient()
    shows = await client.get_trending_shows(limit=limit, page=page)
    return ShowFormatters.format_trending_shows(shows)


@handle_api_errors_func
async def fetch_popular_shows(
    limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Fetch popular shows from Trakt.

    Args:
        limit: Items per page (default: 10)
        page: Page number (optional). If None, returns all results via auto-pagination.

    Returns:
        Information about popular shows. When page is None, returns all shows.
        When page is specified, returns shows from that page with pagination metadata.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = LimitOnly(limit=limit, page=page)
    limit, page = params.limit, params.page

    client = PopularShowsClient()
    shows = await client.get_popular_shows(limit=limit, page=page)
    return ShowFormatters.format_popular_shows(shows)


@handle_api_errors_func
async def fetch_favorited_shows(
    limit: int = DEFAULT_LIMIT,
    period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
    page: int | None = None,
) -> str:
    """Fetch most favorited shows from Trakt.

    Args:
        limit: Items per page (default: 10)
        period: Time period for favorite calculation (daily, weekly, monthly, yearly, all)
        page: Page number (optional). If None, returns all results via auto-pagination.

    Returns:
        Information about most favorited shows. When page is None, returns all shows.
        When page is specified, returns shows from that page with pagination metadata.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = PeriodParams(limit=limit, period=period, page=page)
    limit, period, page = params.limit, params.period, params.page

    client = ShowStatsClient()
    shows = await client.get_favorited_shows(limit=limit, period=period, page=page)

    # Trace structure in debug only (only for list responses to avoid pagination object)
    if shows and isinstance(shows, list):
        logger.debug(
            "Favorited shows API response structure: %s",
            json.dumps(shows[0], indent=2),
        )

    return ShowFormatters.format_favorited_shows(shows)


@handle_api_errors_func
async def fetch_played_shows(
    limit: int = DEFAULT_LIMIT,
    period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
    page: int | None = None,
) -> str:
    """Fetch most played shows from Trakt.

    Args:
        limit: Items per page (default: 10)
        period: Time period for most played (daily, weekly, monthly, yearly, all)
        page: Page number (optional). If None, returns all results via auto-pagination.

    Returns:
        Information about most played shows. When page is None, returns all shows.
        When page is specified, returns shows from that page with pagination metadata.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = PeriodParams(limit=limit, period=period, page=page)
    limit, period, page = params.limit, params.period, params.page

    client = ShowStatsClient()
    shows = await client.get_played_shows(limit=limit, period=period, page=page)
    return ShowFormatters.format_played_shows(shows)


@handle_api_errors_func
async def fetch_watched_shows(
    limit: int = DEFAULT_LIMIT,
    period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
    page: int | None = None,
) -> str:
    """Fetch most watched shows from Trakt.

    Args:
        limit: Items per page (default: 10)
        period: Time period for most watched (daily, weekly, monthly, yearly, all)
        page: Page number (optional). If None, returns all results via auto-pagination.

    Returns:
        Information about most watched shows. When page is None, returns all shows.
        When page is specified, returns shows from that page with pagination metadata.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = PeriodParams(limit=limit, period=period, page=page)
    limit, period, page = params.limit, params.period, params.page

    client = ShowStatsClient()
    shows = await client.get_watched_shows(limit=limit, period=period, page=page)
    return ShowFormatters.format_watched_shows(shows)


@handle_api_errors_func
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
    # Validate required parameters via Pydantic
    params = ShowIdParam(show_id=show_id)
    show_id = params.show_id

    try:
        client: ShowDetailsClient = ShowDetailsClient()
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


@handle_api_errors_func
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
    # Validate required parameters via Pydantic
    params = ShowSummaryParams(show_id=show_id, extended=extended)
    show_id, extended = params.show_id, params.extended

    try:
        client: ShowDetailsClient = ShowDetailsClient()

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


@handle_api_errors_func
async def fetch_show_videos(show_id: str, embed_markdown: bool = True) -> str:
    """Fetch videos for a show from Trakt.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        embed_markdown: Use embedded markdown syntax for video links

    Returns:
        Markdown formatted list of videos
    """
    # Validate required parameters via Pydantic
    params = ShowVideoParams(show_id=show_id, embed_markdown=embed_markdown)
    show_id, embed_markdown = params.show_id, params.embed_markdown

    try:
        client: ShowsClient = ShowsClient()  # Use unified client
        videos = await client.get_videos(show_id)

        # Get show title for context, fallback to ID if fetch fails
        try:
            show = await client.get_show(show_id)

            # Transitional case where API may return error strings; don't fail the tool
            if isinstance(show, str):
                logger.debug(
                    "Show lookup returned API error; falling back to ID title.",
                    extra={
                        "resource_type": "show",
                        "resource_id": show_id,
                        "api_error_message": show,
                        "operation": "fetch_show_for_videos",
                    },
                )
                title = f"Show ID: {show_id}"
            else:
                title = show.get("title", f"Show ID: {show_id}")
        except Exception:
            # Best-effort title lookup — don't fail the operation
            logger.debug(
                "Non-fatal exception during show title lookup; falling back to ID title.",
                exc_info=True,
                extra={"resource_id": show_id, "operation": "fetch_show_for_videos"},
            )
            # Use show_id as fallback title if show fetch fails
            title = f"Show ID: {show_id}"

        return VideoFormatters.format_videos_list(
            videos, title, embed_markdown, validate_input=False
        )
    except MCPError:
        raise


def register_show_tools(mcp: FastMCP) -> tuple[ToolHandler, ...]:
    """Register show tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_trending_shows"],
        description="Fetch trending TV shows from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_trending_shows_tool(
        limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> str:
        # Validate parameters with Pydantic
        params = LimitOnly(limit=limit, page=page)
        return await fetch_trending_shows(params.limit, params.page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_popular_shows"],
        description="Fetch popular TV shows from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_popular_shows_tool(
        limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> str:
        # Validate parameters with Pydantic
        params = LimitOnly(limit=limit, page=page)
        return await fetch_popular_shows(params.limit, params.page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_favorited_shows"],
        description="Fetch most favorited TV shows from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_favorited_shows_tool(
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
    ) -> str:
        # Validate parameters with Pydantic
        params = PeriodParams(limit=limit, period=period, page=page)
        return await fetch_favorited_shows(params.limit, params.period, params.page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_played_shows"],
        description="Fetch most played TV shows from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_played_shows_tool(
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
    ) -> str:
        # Validate parameters with Pydantic
        params = PeriodParams(limit=limit, period=period, page=page)
        return await fetch_played_shows(params.limit, params.period, params.page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_watched_shows"],
        description="Fetch most watched TV shows from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_watched_shows_tool(
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
    ) -> str:
        # Validate parameters with Pydantic
        params = PeriodParams(limit=limit, period=period, page=page)
        return await fetch_watched_shows(params.limit, params.period, params.page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_show_ratings"],
        description="Fetch ratings and voting statistics for a specific TV show",
    )
    @handle_api_errors_func
    async def fetch_show_ratings_tool(show_id: str) -> str:
        # Validate parameters with Pydantic
        params = ShowIdParam(show_id=show_id)
        return await fetch_show_ratings(params.show_id)

    @mcp.tool(
        name=TOOL_NAMES["fetch_show_summary"],
        description="Get TV show summary from Trakt. Default behavior (extended=true): Returns comprehensive data including air times, production status, ratings, genres, runtime, network, and metadata. Basic mode (extended=false): Returns only title, year, and Trakt ID.",
    )
    @handle_api_errors_func
    async def fetch_show_summary_tool(show_id: str, extended: bool = True) -> str:
        # Validate parameters with Pydantic
        params = ShowSummaryParams(show_id=show_id, extended=extended)
        return await fetch_show_summary(params.show_id, params.extended)

    @mcp.tool(
        name=TOOL_NAMES["fetch_show_videos"],
        description=(
            "Get videos (trailers, teasers, etc.) for a show from Trakt. "
            "Set embed_markdown=False to return simple links instead of YouTube iframes."
        ),
    )
    @handle_api_errors_func
    async def fetch_show_videos_tool(show_id: str, embed_markdown: bool = True) -> str:
        """MCP tool wrapper for fetch_show_videos."""
        # Validate parameters with Pydantic
        params = ShowVideoParams(show_id=show_id, embed_markdown=embed_markdown)
        return await fetch_show_videos(params.show_id, params.embed_markdown)

    # Return handlers for type checker visibility
    return (
        fetch_trending_shows_tool,
        fetch_popular_shows_tool,
        fetch_favorited_shows_tool,
        fetch_played_shows_tool,
        fetch_watched_shows_tool,
        fetch_show_ratings_tool,
        fetch_show_summary_tool,
        fetch_show_videos_tool,
    )
