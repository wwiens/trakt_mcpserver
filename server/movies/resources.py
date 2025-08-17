"""Movie resources for the Trakt MCP server."""

import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.types import MovieResponse

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from client.movies import MoviesClient
from config.api import DEFAULT_LIMIT
from config.mcp.resources import MCP_RESOURCES
from models.formatters.movies import MovieFormatters
from server.base import BaseToolErrorMixin
from server.movies.tools import MovieIdParam
from utils.api.error_types import TraktValidationError
from utils.api.errors import handle_api_errors_func

logger: logging.Logger = logging.getLogger("trakt_mcp")

# Type alias for resource handler functions
type ResourceHandler = Callable[[], Awaitable[str]]


@handle_api_errors_func
async def get_trending_movies() -> str:
    """Returns the most watched movies over the last 24 hours from Trakt.

    Movies with the most watchers are returned first.

    Returns:
        Formatted markdown text with trending movies
    """
    client = MoviesClient()
    movies = await client.get_trending_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_trending_movies(movies)


@handle_api_errors_func
async def get_popular_movies() -> str:
    """Returns the most popular movies from Trakt.

    Popularity is calculated using the rating percentage and the number of ratings.

    Returns:
        Formatted markdown text with popular movies
    """
    client = MoviesClient()
    movies = await client.get_popular_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_popular_movies(movies)


@handle_api_errors_func
async def get_favorited_movies() -> str:
    """Returns the most favorited movies from Trakt in the specified time period.

    Defaults to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most favorited movies
    """
    client = MoviesClient()
    movies = await client.get_favorited_movies(limit=DEFAULT_LIMIT)

    # Debug log for API response structure analysis
    if movies:
        logger.debug(
            "Favorited movies API response structure",
            extra={
                "first_movie_keys": list(movies[0].keys()),
                "movie_count": len(movies),
                "first_movie_type": type(movies[0]).__name__,
            },
        )

    return MovieFormatters.format_favorited_movies(movies)


@handle_api_errors_func
async def get_played_movies() -> str:
    """Returns the most played movies from Trakt in the specified time period.

    A single user can watch a single movie multiple times. Defaults to weekly.
    All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most played movies
    """
    client = MoviesClient()
    movies = await client.get_played_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_played_movies(movies)


@handle_api_errors_func
async def get_watched_movies() -> str:
    """Returns the most watched (unique users) movies from Trakt.

    Data is from the specified time period, defaulting to weekly.
    All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most watched movies
    """
    client = MoviesClient()
    movies = await client.get_watched_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_watched_movies(movies)


@handle_api_errors_func
async def get_movie_ratings(movie_id: str) -> str:
    """Returns ratings for a specific movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie

    Returns:
        Formatted markdown text with movie ratings

    Raises:
        InvalidParamsError: If movie_id is invalid
        InternalError: If an error occurs fetching movie or ratings data
    """
    client = MoviesClient()

    # Validate parameters with Pydantic for normalization and constraints
    try:
        params = MovieIdParam(movie_id=movie_id)
        movie_id = params.movie_id
    except ValidationError as e:
        error_details = {str(error["loc"][-1]): error["msg"] for error in e.errors()}
        raise TraktValidationError(
            f"Invalid parameters for movie ratings: {', '.join(error_details.keys())}",
            invalid_params=list(error_details.keys()),
            validation_details=error_details,
        ) from e

    movie = await client.get_movie(movie_id)

    # Handle transitional case where API returns error strings
    if isinstance(movie, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="movie",
            resource_id=movie_id,
            error_message=movie,
            operation="fetch_movie_details",
        )

    # Type narrowing: movie is guaranteed to be MovieResponse after string check
    movie_data: "MovieResponse" = movie
    movie_title = movie_data["title"]

    ratings = await client.get_movie_ratings(movie_id)

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


def register_movie_resources(
    mcp: FastMCP,
) -> tuple[
    ResourceHandler, ResourceHandler, ResourceHandler, ResourceHandler, ResourceHandler
]:
    """Register movie resources with the MCP server.

    Returns:
        Tuple of resource handlers for type checker visibility
    """

    @mcp.resource(
        uri=MCP_RESOURCES["movies_trending"],
        name="movies_trending",
        description="Most watched movies over the last 24 hours from Trakt",
        mime_type="text/markdown",
    )
    async def movies_trending_resource() -> str:
        return await get_trending_movies()

    @mcp.resource(
        uri=MCP_RESOURCES["movies_popular"],
        name="movies_popular",
        description="Most popular movies from Trakt based on ratings and votes",
        mime_type="text/markdown",
    )
    async def movies_popular_resource() -> str:
        return await get_popular_movies()

    @mcp.resource(
        uri=MCP_RESOURCES["movies_favorited"],
        name="movies_favorited",
        description="Most favorited movies from Trakt in the current weekly period",
        mime_type="text/markdown",
    )
    async def movies_favorited_resource() -> str:
        return await get_favorited_movies()

    @mcp.resource(
        uri=MCP_RESOURCES["movies_played"],
        name="movies_played",
        description="Most played movies from Trakt in the current weekly period",
        mime_type="text/markdown",
    )
    async def movies_played_resource() -> str:
        return await get_played_movies()

    @mcp.resource(
        uri=MCP_RESOURCES["movies_watched"],
        name="movies_watched",
        description="Most watched movies by unique users from Trakt in the current weekly period",
        mime_type="text/markdown",
    )
    async def movies_watched_resource() -> str:
        return await get_watched_movies()

    # Note: movie_ratings moved to tools.py as @mcp.tool since it requires parameters

    # Return handlers for type checker visibility
    return (
        movies_trending_resource,
        movies_popular_resource,
        movies_favorited_resource,
        movies_played_resource,
        movies_watched_resource,
    )
