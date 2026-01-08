"""MCP tools for Trakt recommendations."""

import logging
from collections.abc import Awaitable, Callable

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from client.recommendations import RecommendationsClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.recommendations import RecommendationFormatters
from server.base import BaseToolErrorMixin
from utils.api.errors import handle_api_errors_func

logger = logging.getLogger("trakt_mcp")

# Type alias for tool handlers
ToolHandler = Callable[..., Awaitable[str]]


class RecommendationParams(BaseModel):
    """Parameters for recommendation fetching."""

    limit: int = Field(DEFAULT_LIMIT, ge=1, le=100)
    page: int | None = Field(default=None, ge=1)
    ignore_collected: bool = Field(
        default=True,
        description="Filter out items the user has already collected",
    )
    ignore_watchlisted: bool = Field(
        default=True,
        description="Filter out items the user has already watchlisted",
    )

    @field_validator("page", mode="before")
    @classmethod
    def _validate_page(cls, v: object) -> object:
        if v is None or v == "":
            return None
        return v


class HideRecommendationParams(BaseModel):
    """Parameters for hiding a recommendation."""

    item_id: str = Field(..., min_length=1, description="Trakt ID, slug, or IMDB ID")

    @field_validator("item_id", mode="before")
    @classmethod
    def _strip_id(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


@handle_api_errors_func
async def fetch_movie_recommendations(
    limit: int = DEFAULT_LIMIT,
    page: int | None = None,
    ignore_collected: bool = True,
    ignore_watchlisted: bool = True,
) -> str:
    """Fetch personalized movie recommendations from Trakt.

    Args:
        limit: Number of results per page (max 100).
        page: Page number. If None, auto-paginates all results.
        ignore_collected: Filter out movies user has collected.
        ignore_watchlisted: Filter out movies user has watchlisted.

    Returns:
        Formatted markdown with movie recommendations.

    Raises:
        AuthenticationRequiredError: If user is not authenticated.
    """
    logger.debug(
        "fetch_movie_recommendations called with limit=%s, page=%s", limit, page
    )
    params = RecommendationParams(
        limit=limit,
        page=page,
        ignore_collected=ignore_collected,
        ignore_watchlisted=ignore_watchlisted,
    )

    client = RecommendationsClient()
    recommendations = await client.get_movie_recommendations(
        limit=params.limit,
        page=params.page,
        ignore_collected=params.ignore_collected,
        ignore_watchlisted=params.ignore_watchlisted,
    )

    # Handle transitional case where API returns error strings
    if isinstance(recommendations, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="movie_recommendations",
            resource_id="recommendations",
            error_message=recommendations,
            operation="fetch_movie_recommendations",
        )

    return RecommendationFormatters.format_movie_recommendations(recommendations)


@handle_api_errors_func
async def fetch_show_recommendations(
    limit: int = DEFAULT_LIMIT,
    page: int | None = None,
    ignore_collected: bool = True,
    ignore_watchlisted: bool = True,
) -> str:
    """Fetch personalized show recommendations from Trakt.

    Args:
        limit: Number of results per page (max 100).
        page: Page number. If None, auto-paginates all results.
        ignore_collected: Filter out shows user has collected.
        ignore_watchlisted: Filter out shows user has watchlisted.

    Returns:
        Formatted markdown with show recommendations.

    Raises:
        AuthenticationRequiredError: If user is not authenticated.
    """
    logger.debug(
        "fetch_show_recommendations called with limit=%s, page=%s", limit, page
    )
    params = RecommendationParams(
        limit=limit,
        page=page,
        ignore_collected=ignore_collected,
        ignore_watchlisted=ignore_watchlisted,
    )

    client = RecommendationsClient()
    recommendations = await client.get_show_recommendations(
        limit=params.limit,
        page=params.page,
        ignore_collected=params.ignore_collected,
        ignore_watchlisted=params.ignore_watchlisted,
    )

    # Handle transitional case where API returns error strings
    if isinstance(recommendations, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="show_recommendations",
            resource_id="recommendations",
            error_message=recommendations,
            operation="fetch_show_recommendations",
        )

    return RecommendationFormatters.format_show_recommendations(recommendations)


@handle_api_errors_func
async def hide_movie_recommendation(movie_id: str) -> str:
    """Hide a movie from future recommendations.

    Args:
        movie_id: Trakt ID, slug, or IMDB ID.

    Returns:
        Formatted success message.

    Raises:
        AuthenticationRequiredError: If user is not authenticated.
    """
    logger.debug("hide_movie_recommendation called with movie_id=%s", movie_id)
    params = HideRecommendationParams(item_id=movie_id)

    client = RecommendationsClient()
    await client.hide_movie_recommendation(params.item_id)
    return RecommendationFormatters.format_hide_result("movie", params.item_id)


@handle_api_errors_func
async def hide_show_recommendation(show_id: str) -> str:
    """Hide a show from future recommendations.

    Args:
        show_id: Trakt ID, slug, or IMDB ID.

    Returns:
        Formatted success message.

    Raises:
        AuthenticationRequiredError: If user is not authenticated.
    """
    logger.debug("hide_show_recommendation called with show_id=%s", show_id)
    params = HideRecommendationParams(item_id=show_id)

    client = RecommendationsClient()
    await client.hide_show_recommendation(params.item_id)
    return RecommendationFormatters.format_hide_result("show", params.item_id)


@handle_api_errors_func
async def unhide_movie_recommendation(movie_id: str) -> str:
    """Unhide a movie to restore it in future recommendations.

    Args:
        movie_id: Trakt ID, slug, or IMDB ID.

    Returns:
        Formatted success message.

    Raises:
        AuthenticationRequiredError: If user is not authenticated.
    """
    logger.debug("unhide_movie_recommendation called with movie_id=%s", movie_id)
    params = HideRecommendationParams(item_id=movie_id)

    client = RecommendationsClient()
    await client.unhide_movie_recommendation(params.item_id)
    return RecommendationFormatters.format_unhide_result("movie", params.item_id)


@handle_api_errors_func
async def unhide_show_recommendation(show_id: str) -> str:
    """Unhide a show to restore it in future recommendations.

    Args:
        show_id: Trakt ID, slug, or IMDB ID.

    Returns:
        Formatted success message.

    Raises:
        AuthenticationRequiredError: If user is not authenticated.
    """
    logger.debug("unhide_show_recommendation called with show_id=%s", show_id)
    params = HideRecommendationParams(item_id=show_id)

    client = RecommendationsClient()
    await client.unhide_show_recommendation(params.item_id)
    return RecommendationFormatters.format_unhide_result("show", params.item_id)


def register_recommendation_tools(
    mcp: FastMCP,
) -> tuple[
    ToolHandler, ToolHandler, ToolHandler, ToolHandler, ToolHandler, ToolHandler
]:
    """Register recommendation tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility.
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_movie_recommendations"],
        description=(
            "Fetch personalized movie recommendations from Trakt based on your "
            "viewing history. Requires OAuth authentication. Use page parameter "
            "for paginated results, or omit for all results."
        ),
    )
    async def fetch_movie_recommendations_tool(
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        ignore_collected: bool = True,
        ignore_watchlisted: bool = True,
    ) -> str:
        """MCP tool: fetch personalized movie recommendations."""
        params = RecommendationParams(
            limit=limit,
            page=page,
            ignore_collected=ignore_collected,
            ignore_watchlisted=ignore_watchlisted,
        )
        return await fetch_movie_recommendations(
            params.limit,
            params.page,
            params.ignore_collected,
            params.ignore_watchlisted,
        )

    @mcp.tool(
        name=TOOL_NAMES["fetch_show_recommendations"],
        description=(
            "Fetch personalized TV show recommendations from Trakt based on your "
            "viewing history. Requires OAuth authentication. Use page parameter "
            "for paginated results, or omit for all results."
        ),
    )
    async def fetch_show_recommendations_tool(
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        ignore_collected: bool = True,
        ignore_watchlisted: bool = True,
    ) -> str:
        """MCP tool: fetch personalized show recommendations."""
        params = RecommendationParams(
            limit=limit,
            page=page,
            ignore_collected=ignore_collected,
            ignore_watchlisted=ignore_watchlisted,
        )
        return await fetch_show_recommendations(
            params.limit,
            params.page,
            params.ignore_collected,
            params.ignore_watchlisted,
        )

    @mcp.tool(
        name=TOOL_NAMES["hide_movie_recommendation"],
        description=(
            "Hide a movie from future recommendations. Requires OAuth authentication. "
            "Use Trakt ID, slug, or IMDB ID to identify the movie."
        ),
    )
    async def hide_movie_recommendation_tool(movie_id: str) -> str:
        """MCP tool: hide a movie from future recommendations."""
        return await hide_movie_recommendation(movie_id)

    @mcp.tool(
        name=TOOL_NAMES["hide_show_recommendation"],
        description=(
            "Hide a TV show from future recommendations. Requires OAuth authentication. "
            "Use Trakt ID, slug, or IMDB ID to identify the show."
        ),
    )
    async def hide_show_recommendation_tool(show_id: str) -> str:
        """MCP tool: hide a show from future recommendations."""
        return await hide_show_recommendation(show_id)

    @mcp.tool(
        name=TOOL_NAMES["unhide_movie_recommendation"],
        description=(
            "Unhide a movie to restore it in future recommendations. "
            "Requires OAuth authentication. "
            "Use Trakt ID, slug, or IMDB ID to identify the movie."
        ),
    )
    async def unhide_movie_recommendation_tool(movie_id: str) -> str:
        """MCP tool: unhide a movie to restore it in recommendations."""
        return await unhide_movie_recommendation(movie_id)

    @mcp.tool(
        name=TOOL_NAMES["unhide_show_recommendation"],
        description=(
            "Unhide a TV show to restore it in future recommendations. "
            "Requires OAuth authentication. "
            "Use Trakt ID, slug, or IMDB ID to identify the show."
        ),
    )
    async def unhide_show_recommendation_tool(show_id: str) -> str:
        """MCP tool: unhide a show to restore it in recommendations."""
        return await unhide_show_recommendation(show_id)

    # Return handlers for type checker visibility
    return (
        fetch_movie_recommendations_tool,
        fetch_show_recommendations_tool,
        hide_movie_recommendation_tool,
        hide_show_recommendation_tool,
        unhide_movie_recommendation_tool,
        unhide_show_recommendation_tool,
    )
