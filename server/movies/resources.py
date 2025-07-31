# pyright: reportUnusedFunction=none
"""Movie resources for the Trakt MCP server."""

from mcp.server.fastmcp import FastMCP

from client.movies import MoviesClient
from config.api import DEFAULT_LIMIT
from config.mcp.resources import MCP_RESOURCES
from models.formatters.movies import MovieFormatters


async def get_trending_movies() -> str:
    """Returns the most watched movies over the last 24 hours from Trakt. Movies with the most watchers are returned first.

    Returns:
        Formatted markdown text with trending movies
    """
    client = MoviesClient()
    movies = await client.get_trending_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_trending_movies(movies)


async def get_popular_movies() -> str:
    """Returns the most popular movies from Trakt. Popularity is calculated using the rating percentage and the number of ratings.

    Returns:
        Formatted markdown text with popular movies
    """
    client = MoviesClient()
    movies = await client.get_popular_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_popular_movies(movies)


async def get_favorited_movies() -> str:
    """Returns the most favorited movies from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most favorited movies
    """
    client = MoviesClient()
    movies = await client.get_favorited_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_favorited_movies(movies)


async def get_played_movies() -> str:
    """Returns the most played (a single user can watch a single movie multiple times) movies from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most played movies
    """
    client = MoviesClient()
    movies = await client.get_played_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_played_movies(movies)


async def get_watched_movies() -> str:
    """Returns the most watched (unique users) movies from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.

    Returns:
        Formatted markdown text with most watched movies
    """
    client = MoviesClient()
    movies = await client.get_watched_movies(limit=DEFAULT_LIMIT)
    return MovieFormatters.format_watched_movies(movies)


async def get_movie_ratings(movie_id: str) -> str:
    """Returns ratings for a specific movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie

    Returns:
        Formatted markdown text with movie ratings
    """
    client = MoviesClient()
    movie = await client.get_movie(movie_id)

    movie_title = movie.get("title", f"Movie ID: {movie_id}")

    ratings = await client.get_movie_ratings(movie_id)

    return MovieFormatters.format_movie_ratings(ratings, movie_title)


def register_movie_resources(mcp: FastMCP) -> None:
    """Register movie resources with the MCP server."""

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
