# pyright: reportUnusedFunction=none
"""Movie tools for the Trakt MCP server."""

import json
import logging

from mcp.server.fastmcp import FastMCP

from client.movies import MoviesClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.movies import MovieFormatters

logger = logging.getLogger("trakt_mcp")


async def fetch_trending_movies(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch trending movies from Trakt.

    Args:
        limit: Maximum number of movies to return

    Returns:
        Information about trending movies
    """
    client = MoviesClient()
    movies = await client.get_trending_movies(limit=limit)
    return MovieFormatters.format_trending_movies(movies)


async def fetch_popular_movies(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch popular movies from Trakt.

    Args:
        limit: Maximum number of movies to return

    Returns:
        Information about popular movies
    """
    client = MoviesClient()
    movies = await client.get_popular_movies(limit=limit)
    return MovieFormatters.format_popular_movies(movies)


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
    client = MoviesClient()
    movies = await client.get_favorited_movies(limit=limit, period=period)

    # Log the first movie to see the structure
    if movies and len(movies) > 0:
        logger.info(
            f"Favorited movies API response structure: {json.dumps(movies[0], indent=2)}"
        )

    return MovieFormatters.format_favorited_movies(movies)


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
    client = MoviesClient()
    movies = await client.get_played_movies(limit=limit, period=period)
    return MovieFormatters.format_played_movies(movies)


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
    client = MoviesClient()
    movies = await client.get_watched_movies(limit=limit, period=period)
    return MovieFormatters.format_watched_movies(movies)


async def fetch_movie_ratings(movie_id: str) -> str:
    """Fetch ratings for a movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie

    Returns:
        Information about movie ratings including average and distribution
    """
    client = MoviesClient()

    try:
        movie = await client.get_movie(movie_id)

        # Check if the API returned an error string
        if isinstance(movie, str):
            return f"Error fetching ratings for movie ID {movie_id}: {movie}"

        movie_title = movie.get("title", f"Movie ID: {movie_id}")

        ratings = await client.get_movie_ratings(movie_id)

        # Check if the API returned an error string
        if isinstance(ratings, str):
            return f"Error fetching ratings for {movie_title}: {ratings}"

        return MovieFormatters.format_movie_ratings(ratings, movie_title)
    except Exception as e:
        logger.error(f"Error fetching movie ratings: {e}")
        return f"Error fetching ratings for movie ID {movie_id}: {e!s}"


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
    """
    client = MoviesClient()

    try:
        if extended:
            movie = await client.get_movie_extended(movie_id)
            # Check if the API returned an error string
            if isinstance(movie, str):
                return f"Error fetching movie summary for ID {movie_id}: {movie}"
            return MovieFormatters.format_movie_extended(movie)
        else:
            movie = await client.get_movie(movie_id)
            # Check if the API returned an error string
            if isinstance(movie, str):
                return f"Error fetching movie summary for ID {movie_id}: {movie}"
            return MovieFormatters.format_movie_summary(movie)
    except Exception as e:
        logger.error(f"Error fetching movie summary: {e}")
        return f"Error fetching movie summary for ID {movie_id}: {e!s}"


def register_movie_tools(mcp: FastMCP) -> None:
    """Register movie tools with the MCP server."""

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
