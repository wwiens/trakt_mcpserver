"""Movie tools for the Trakt MCP server."""

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.server.fastmcp import FastMCP

from client.movies.details import MovieDetailsClient
from client.movies.popular import PopularMoviesClient
from client.movies.stats import MovieStatsClient
from client.movies.trending import TrendingMoviesClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.movies import MovieFormatters
from server.base import BaseToolErrorMixin

if TYPE_CHECKING:
    from models.types import MovieResponse, TraktRating, TrendingWrapper

logger = logging.getLogger("trakt_mcp")


async def fetch_trending_movies(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch trending movies from Trakt.

    Args:
        limit: Maximum number of movies to return

    Returns:
        Information about trending movies
    """
    # Validate parameters first
    BaseToolErrorMixin.validate_required_params(limit=limit)

    try:
        client = TrendingMoviesClient()
        movies: list[TrendingWrapper] = await client.get_trending_movies(limit=limit)
        return MovieFormatters.format_trending_movies(movies)

    except Exception as e:
        raise BaseToolErrorMixin.handle_unexpected_error(
            "fetch trending movies", e, limit=limit
        ) from e


async def fetch_popular_movies(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch popular movies from Trakt.

    Args:
        limit: Maximum number of movies to return

    Returns:
        Information about popular movies
    """
    # Validate parameters first
    BaseToolErrorMixin.validate_required_params(limit=limit)

    try:
        client = PopularMoviesClient()
        movies: list[MovieResponse] = await client.get_popular_movies(limit=limit)
        return MovieFormatters.format_popular_movies(movies)

    except Exception as e:
        raise BaseToolErrorMixin.handle_unexpected_error(
            "fetch popular movies", e, limit=limit
        ) from e


async def fetch_favorited_movies(
    limit: int = DEFAULT_LIMIT, period: str = "weekly"
) -> str:
    """Fetch most favorited movies from Trakt.

    Args:
        limit: Maximum number of movies to return
        period: Time period for favorite calculation (daily, weekly, monthly, yearly, all)

    Returns:
        Information about most favorited movies
    """
    # Validate parameters first
    BaseToolErrorMixin.validate_required_params(limit=limit, period=period)

    try:
        client = MovieStatsClient()
        movies = await client.get_favorited_movies(limit=limit, period=period)

        # Log the first movie to see the structure
        if movies and len(movies) > 0:
            logger.info(
                f"Favorited movies API response structure: {json.dumps(movies[0], indent=2)}"
            )

        return MovieFormatters.format_favorited_movies(movies)

    except Exception as e:
        raise BaseToolErrorMixin.handle_unexpected_error(
            "fetch favorited movies", e, limit=limit, period=period
        ) from e


async def fetch_played_movies(
    limit: int = DEFAULT_LIMIT, period: str = "weekly"
) -> str:
    """Fetch most played movies from Trakt.

    Args:
        limit: Maximum number of movies to return
        period: Time period for most played (daily, weekly, monthly, yearly, all)

    Returns:
        Information about most played movies
    """
    # Validate parameters first
    BaseToolErrorMixin.validate_required_params(limit=limit, period=period)

    try:
        client = MovieStatsClient()
        movies = await client.get_played_movies(limit=limit, period=period)
        return MovieFormatters.format_played_movies(movies)

    except Exception as e:
        raise BaseToolErrorMixin.handle_unexpected_error(
            "fetch played movies", e, limit=limit, period=period
        ) from e


async def fetch_watched_movies(
    limit: int = DEFAULT_LIMIT, period: str = "weekly"
) -> str:
    """Fetch most watched movies from Trakt.

    Args:
        limit: Maximum number of movies to return
        period: Time period for most watched (daily, weekly, monthly, yearly, all)

    Returns:
        Information about most watched movies
    """
    # Validate parameters first
    BaseToolErrorMixin.validate_required_params(limit=limit, period=period)

    try:
        client = MovieStatsClient()
        movies = await client.get_watched_movies(limit=limit, period=period)
        return MovieFormatters.format_watched_movies(movies)

    except Exception as e:
        raise BaseToolErrorMixin.handle_unexpected_error(
            "fetch watched movies", e, limit=limit, period=period
        ) from e


async def fetch_movie_ratings(movie_id: str) -> str:
    """Fetch ratings for a movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie

    Returns:
        Information about movie ratings including average and distribution

    Raises:
        InvalidParamsError: If movie_id is invalid
        InternalError: If an error occurs fetching movie or ratings data
    """
    # Validate required parameters
    BaseToolErrorMixin.validate_required_params(movie_id=movie_id)

    client = MovieDetailsClient()

    try:
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
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="fetch movie ratings", error=e, movie_id=movie_id
        ) from e


async def fetch_movie_summary(movie_id: str, extended: bool = True) -> str:
    """Fetch movie summary from Trakt.

    Args:
        movie_id: Trakt ID of the movie
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
    # Validate required parameters
    BaseToolErrorMixin.validate_required_params(movie_id=movie_id)

    client = MovieDetailsClient()

    try:
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
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="fetch movie summary",
            error=e,
            movie_id=movie_id,
            extended=extended,
        ) from e


def register_movie_tools(mcp: FastMCP) -> tuple[Any, Any, Any, Any, Any, Any, Any]:
    """Register movie tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_trending_movies"],
        description="Fetch trending movies from Trakt",
    )
    async def fetch_trending_movies_tool(limit: int = DEFAULT_LIMIT) -> str:
        return await fetch_trending_movies(limit)

    @mcp.tool(
        name=TOOL_NAMES["fetch_popular_movies"],
        description="Fetch popular movies from Trakt",
    )
    async def fetch_popular_movies_tool(limit: int = DEFAULT_LIMIT) -> str:
        return await fetch_popular_movies(limit)

    @mcp.tool(
        name=TOOL_NAMES["fetch_favorited_movies"],
        description="Fetch most favorited movies from Trakt",
    )
    async def fetch_favorited_movies_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_favorited_movies(limit, period)

    @mcp.tool(
        name=TOOL_NAMES["fetch_played_movies"],
        description="Fetch most played movies from Trakt",
    )
    async def fetch_played_movies_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_played_movies(limit, period)

    @mcp.tool(
        name=TOOL_NAMES["fetch_watched_movies"],
        description="Fetch most watched movies from Trakt",
    )
    async def fetch_watched_movies_tool(
        limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> str:
        return await fetch_watched_movies(limit, period)

    @mcp.tool(
        name=TOOL_NAMES["fetch_movie_ratings"],
        description="Fetch ratings and voting statistics for a specific movie",
    )
    async def fetch_movie_ratings_tool(movie_id: str) -> str:
        return await fetch_movie_ratings(movie_id)

    @mcp.tool(
        name=TOOL_NAMES["fetch_movie_summary"],
        description="Get movie summary from Trakt. Default behavior (extended=true): Returns comprehensive data including production status, ratings, genres, runtime, certification, and metadata. Basic mode (extended=false): Returns only title, year, and Trakt ID.",
    )
    async def fetch_movie_summary_tool(movie_id: str, extended: bool = True) -> str:
        return await fetch_movie_summary(movie_id, extended)

    # Return handlers for type checker visibility
    return (
        fetch_trending_movies_tool,
        fetch_popular_movies_tool,
        fetch_favorited_movies_tool,
        fetch_played_movies_tool,
        fetch_watched_movies_tool,
        fetch_movie_ratings_tool,
        fetch_movie_summary_tool,
    )
