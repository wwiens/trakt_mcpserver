"""Movie tools for the Trakt MCP server."""

import json
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from client.movies.client import MoviesClient
from client.movies.details import MovieDetailsClient
from client.movies.popular import PopularMoviesClient
from client.movies.stats import MovieStatsClient
from client.movies.trending import TrendingMoviesClient
from config.api import DEFAULT_LIMIT
from config.mcp.descriptions import (
    EMBED_MARKDOWN_DESCRIPTION,
    EXTENDED_DESCRIPTION,
    LIMIT_DESCRIPTION,
    MOVIE_ID_DESCRIPTION,
    PAGE_DESCRIPTION,
    PERIOD_DESCRIPTION,
)
from config.mcp.tools import TOOL_NAMES
from models.formatters.movies import MovieFormatters
from models.formatters.videos import VideoFormatters
from server.base import BaseToolErrorMixin, LimitOnly, PeriodParams
from utils.api.errors import MCPError, handle_api_errors_func

if TYPE_CHECKING:
    from models.types import MovieResponse, TraktRating

logger = logging.getLogger("trakt_mcp")

# Type alias for tool handlers
ToolHandler = Callable[..., Awaitable[str]]


class MovieIdParam(BaseModel):
    """Parameters for tools that require a movie ID."""

    movie_id: str = Field(
        ...,
        min_length=1,
        description=MOVIE_ID_DESCRIPTION,
    )

    @field_validator("movie_id", mode="before")
    @classmethod
    def _strip_movie_id(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


class MovieSummaryParams(MovieIdParam):
    """Parameters for movie summary tools with extended option."""

    extended: bool = True


class MovieVideoParams(MovieIdParam):
    """Parameters for movie video tools."""

    embed_markdown: bool = True


@handle_api_errors_func
async def fetch_trending_movies(
    limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Fetch trending movies from Trakt.

    Args:
        limit: Maximum movies to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        page: Page number. If None, auto-paginates up to 'limit' total movies.
            If specified, returns that page with pagination metadata.

    Returns:
        Information about trending movies.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = LimitOnly(limit=limit, page=page)
    limit, page = params.limit, params.page

    client = TrendingMoviesClient()
    movies = await client.get_trending_movies(limit=limit, page=page)
    return MovieFormatters.format_trending_movies(movies)


@handle_api_errors_func
async def fetch_popular_movies(
    limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Fetch popular movies from Trakt.

    Args:
        limit: Maximum movies to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        page: Page number. If None, auto-paginates up to 'limit' total movies.
            If specified, returns that page with pagination metadata.

    Returns:
        Information about popular movies.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = LimitOnly(limit=limit, page=page)
    limit, page = params.limit, params.page

    client = PopularMoviesClient()
    movies = await client.get_popular_movies(limit=limit, page=page)
    return MovieFormatters.format_popular_movies(movies)


@handle_api_errors_func
async def fetch_favorited_movies(
    limit: int = DEFAULT_LIMIT,
    period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
    page: int | None = None,
) -> str:
    """Fetch most favorited movies from Trakt.

    Args:
        limit: Maximum movies to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        period: Time period for favorite calculation (daily, weekly, monthly, yearly, all)
        page: Page number. If None, auto-paginates up to 'limit' total movies.
            If specified, returns that page with pagination metadata.

    Returns:
        Information about most favorited movies.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = PeriodParams(limit=limit, period=period, page=page)
    limit, period, page = params.limit, params.period, params.page

    client = MovieStatsClient()
    movies = await client.get_favorited_movies(limit=limit, period=period, page=page)

    # Trace structure in debug only (only for list responses to avoid pagination object)
    if movies and isinstance(movies, list):
        logger.debug(
            "Favorited movies API response structure: %s",
            json.dumps(movies[0], indent=2),
        )

    return MovieFormatters.format_favorited_movies(movies)


@handle_api_errors_func
async def fetch_played_movies(
    limit: int = DEFAULT_LIMIT,
    period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
    page: int | None = None,
) -> str:
    """Fetch most played movies from Trakt.

    Args:
        limit: Maximum movies to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        period: Time period for most played (daily, weekly, monthly, yearly, all)
        page: Page number. If None, auto-paginates up to 'limit' total movies.
            If specified, returns that page with pagination metadata.

    Returns:
        Information about most played movies.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = PeriodParams(limit=limit, period=period, page=page)
    limit, period, page = params.limit, params.period, params.page

    client = MovieStatsClient()
    movies = await client.get_played_movies(limit=limit, period=period, page=page)
    return MovieFormatters.format_played_movies(movies)


@handle_api_errors_func
async def fetch_watched_movies(
    limit: int = DEFAULT_LIMIT,
    period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
    page: int | None = None,
) -> str:
    """Fetch most watched movies from Trakt.

    Args:
        limit: Maximum movies to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        period: Time period for most watched (daily, weekly, monthly, yearly, all)
        page: Page number. If None, auto-paginates up to 'limit' total movies.
            If specified, returns that page with pagination metadata.

    Returns:
        Information about most watched movies.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = PeriodParams(limit=limit, period=period, page=page)
    limit, period, page = params.limit, params.period, params.page

    client = MovieStatsClient()
    movies = await client.get_watched_movies(limit=limit, period=period, page=page)
    return MovieFormatters.format_watched_movies(movies)


@handle_api_errors_func
async def fetch_movie_ratings(movie_id: str) -> str:
    """Fetch ratings for a movie from Trakt.

    Args:
        movie_id: Trakt ID, Trakt slug, or IMDB ID (e.g., '1', 'tron-legacy-2010', 'tt1104001')

    Returns:
        Information about movie ratings including average and distribution

    Raises:
        InvalidParamsError: If movie_id is invalid
        InternalError: If an error occurs fetching movie or ratings data
    """
    # Validate required parameters via Pydantic
    params = MovieIdParam(movie_id=movie_id)
    movie_id = params.movie_id

    try:
        client = MovieDetailsClient()
        movie: MovieResponse = await client.get_movie(movie_id)

        # Handle transitional case where API returns error strings
        if isinstance(movie, str):
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type="movie",
                resource_id=movie_id,
                error_message=movie,
                operation="fetch_movie_details",
            )

        movie_title = movie.get("title", f"Movie ID: {movie_id}")

        ratings: TraktRating = await client.get_movie_ratings(movie_id)

        # Handle transitional case where API returns error strings
        if isinstance(ratings, str):
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type="movie_ratings",
                resource_id=movie_id,
                error_message=ratings,
                operation="fetch_movie_ratings",
                movie_title=movie_title,
            )

        return MovieFormatters.format_movie_ratings(ratings, movie_title)
    except MCPError:
        raise


@handle_api_errors_func
async def fetch_movie_summary(movie_id: str, extended: bool = True) -> str:
    """Fetch movie summary from Trakt.

    Args:
        movie_id: Trakt ID, Trakt slug, or IMDB ID (e.g., '1', 'tron-legacy-2010', 'tt1104001')
        extended: If True, return comprehensive data with production status and metadata.
                 If False, return basic movie information (title, year, IDs).

    Returns:
        Movie information formatted as markdown. Extended mode includes production status,
        ratings, metadata, and detailed information. Basic mode includes title, year,
        and Trakt ID only.

    Raises:
        InvalidParamsError: If movie_id is invalid
        InternalError: If an error occurs fetching movie data
    """
    # Validate required parameters via Pydantic
    params = MovieSummaryParams(movie_id=movie_id, extended=extended)
    movie_id, extended = params.movie_id, params.extended

    try:
        client = MovieDetailsClient()
        if extended:
            movie: MovieResponse = await client.get_movie_extended(movie_id)
            # Handle transitional case where API returns error strings
            if isinstance(movie, str):
                raise BaseToolErrorMixin.handle_api_string_error(
                    resource_type="movie_extended",
                    resource_id=movie_id,
                    error_message=movie,
                    operation="fetch_movie_extended",
                )
            return MovieFormatters.format_movie_extended(movie)
        else:
            movie: MovieResponse = await client.get_movie(movie_id)
            # Handle transitional case where API returns error strings
            if isinstance(movie, str):
                raise BaseToolErrorMixin.handle_api_string_error(
                    resource_type="movie",
                    resource_id=movie_id,
                    error_message=movie,
                    operation="fetch_movie_summary",
                )
            return MovieFormatters.format_movie_summary(movie)
    except MCPError:
        raise


@handle_api_errors_func
async def fetch_movie_videos(movie_id: str, embed_markdown: bool = True) -> str:
    """Fetch videos for a movie from Trakt.

    Args:
        movie_id: Trakt ID, Trakt slug, or IMDB ID (e.g., '1', 'tron-legacy-2010', 'tt1104001')
        embed_markdown: Use embedded markdown syntax for video links

    Returns:
        Markdown formatted list of videos
    """
    # Validate required parameters via Pydantic
    params = MovieVideoParams(movie_id=movie_id, embed_markdown=embed_markdown)
    movie_id, embed_markdown = params.movie_id, params.embed_markdown

    try:
        client: MoviesClient = MoviesClient()  # Use unified client
        videos = await client.get_videos(movie_id)
        # Transitional safeguard if client returns string errors
        if isinstance(videos, str):
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type="movie_videos",
                resource_id=movie_id,
                error_message=videos,
                operation="fetch_movie_videos",
            )

        # Get movie title for context, fallback to ID if fetch fails
        try:
            movie = await client.get_movie(movie_id)

            # Handle transitional case where API returns error strings
            if isinstance(movie, str):
                raise BaseToolErrorMixin.handle_api_string_error(
                    resource_type="movie",
                    resource_id=movie_id,
                    error_message=movie,
                    operation="fetch_movie_for_videos",
                )

            title = movie.get("title", f"Movie ID: {movie_id}")
        except Exception as e:
            # Best-effort title lookup - don't fail the whole operation
            logger.debug(
                "Non-fatal exception during movie title lookup: %s (movie_id: %s)",
                str(e),
                movie_id,
                exc_info=True,
            )
            # Use movie_id as fallback title if movie fetch fails
            title = f"Movie ID: {movie_id}"

        return VideoFormatters.format_videos_list(
            videos, title, embed_markdown, validate_input=False
        )
    except MCPError:
        raise


def register_movie_tools(mcp: FastMCP) -> tuple[ToolHandler, ...]:
    """Register movie tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_trending_movies"],
        description="Fetch trending movies from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_trending_movies_tool(
        limit: Annotated[int, Field(description=LIMIT_DESCRIPTION)] = DEFAULT_LIMIT,
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await fetch_trending_movies(limit, page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_popular_movies"],
        description="Fetch popular movies from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_popular_movies_tool(
        limit: Annotated[int, Field(description=LIMIT_DESCRIPTION)] = DEFAULT_LIMIT,
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await fetch_popular_movies(limit, page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_favorited_movies"],
        description="Fetch most favorited movies from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_favorited_movies_tool(
        limit: Annotated[int, Field(description=LIMIT_DESCRIPTION)] = DEFAULT_LIMIT,
        period: Annotated[
            Literal["daily", "weekly", "monthly", "yearly", "all"],
            Field(description=PERIOD_DESCRIPTION),
        ] = "weekly",
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await fetch_favorited_movies(limit, period, page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_played_movies"],
        description="Fetch most played movies from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_played_movies_tool(
        limit: Annotated[int, Field(description=LIMIT_DESCRIPTION)] = DEFAULT_LIMIT,
        period: Annotated[
            Literal["daily", "weekly", "monthly", "yearly", "all"],
            Field(description=PERIOD_DESCRIPTION),
        ] = "weekly",
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await fetch_played_movies(limit, period, page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_watched_movies"],
        description="Fetch most watched movies from Trakt. Use page parameter for paginated results, or omit for all results.",
    )
    @handle_api_errors_func
    async def fetch_watched_movies_tool(
        limit: Annotated[int, Field(description=LIMIT_DESCRIPTION)] = DEFAULT_LIMIT,
        period: Annotated[
            Literal["daily", "weekly", "monthly", "yearly", "all"],
            Field(description=PERIOD_DESCRIPTION),
        ] = "weekly",
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await fetch_watched_movies(limit, period, page)

    @mcp.tool(
        name=TOOL_NAMES["fetch_movie_ratings"],
        description="Fetch ratings and voting statistics for a specific movie",
    )
    @handle_api_errors_func
    async def fetch_movie_ratings_tool(
        movie_id: Annotated[str, Field(min_length=1, description=MOVIE_ID_DESCRIPTION)],
    ) -> str:
        # Validate parameters with Pydantic
        params = MovieIdParam(movie_id=movie_id)
        return await fetch_movie_ratings(params.movie_id)

    @mcp.tool(
        name=TOOL_NAMES["fetch_movie_summary"],
        description="Get movie summary from Trakt. Default behavior (extended=true): Returns comprehensive data including production status, ratings, genres, runtime, certification, and metadata. Basic mode (extended=false): Returns only title, year, and Trakt ID.",
    )
    @handle_api_errors_func
    async def fetch_movie_summary_tool(
        movie_id: Annotated[str, Field(min_length=1, description=MOVIE_ID_DESCRIPTION)],
        extended: Annotated[bool, Field(description=EXTENDED_DESCRIPTION)] = True,
    ) -> str:
        # Validate parameters with Pydantic
        params = MovieSummaryParams(movie_id=movie_id, extended=extended)
        return await fetch_movie_summary(params.movie_id, params.extended)

    @mcp.tool(
        name=TOOL_NAMES["fetch_movie_videos"],
        description=(
            "Get videos (trailers, teasers, etc.) for a movie from Trakt. "
            "Set embed_markdown=False to return simple links instead of YouTube iframes."
        ),
    )
    @handle_api_errors_func
    async def fetch_movie_videos_tool(
        movie_id: Annotated[str, Field(min_length=1, description=MOVIE_ID_DESCRIPTION)],
        embed_markdown: Annotated[
            bool,
            Field(description=EMBED_MARKDOWN_DESCRIPTION),
        ] = True,
    ) -> str:
        """MCP tool wrapper for fetch_movie_videos."""
        # Validate parameters with Pydantic
        params = MovieVideoParams(movie_id=movie_id, embed_markdown=embed_markdown)
        return await fetch_movie_videos(params.movie_id, params.embed_markdown)

    # Return handlers for type checker visibility
    return (
        fetch_trending_movies_tool,
        fetch_popular_movies_tool,
        fetch_favorited_movies_tool,
        fetch_played_movies_tool,
        fetch_watched_movies_tool,
        fetch_movie_ratings_tool,
        fetch_movie_summary_tool,
        fetch_movie_videos_tool,
    )
