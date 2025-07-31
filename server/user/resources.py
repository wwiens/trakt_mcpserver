# pyright: reportUnusedFunction=none
"""User resources for the Trakt MCP server."""

from mcp.server.fastmcp import FastMCP

from client.user import UserClient
from config.errors import AUTH_REQUIRED_MARKDOWN
from config.mcp.resources import MCP_RESOURCES
from models.formatters.user import UserFormatters


async def get_user_watched_shows() -> str:
    """Returns shows that the authenticated user has watched.
    Requires authentication with Trakt.

    Returns:
        Formatted markdown text with user's watched shows
    """
    client = UserClient()

    if not client.is_authenticated():
        return AUTH_REQUIRED_MARKDOWN

    shows = await client.get_user_watched_shows()
    return UserFormatters.format_user_watched_shows(shows)


async def get_user_watched_movies() -> str:
    """Returns movies that the authenticated user has watched.
    Requires authentication with Trakt.

    Returns:
        Formatted markdown text with user's watched movies
    """
    client = UserClient()

    if not client.is_authenticated():
        return AUTH_REQUIRED_MARKDOWN

    movies = await client.get_user_watched_movies()
    return UserFormatters.format_user_watched_movies(movies)


def register_user_resources(mcp: FastMCP) -> None:
    """Register user resources with the MCP server."""

    @mcp.resource(
        uri=MCP_RESOURCES["user_watched_shows"],
        name="user_watched_shows",
        description="TV shows watched by the authenticated user from Trakt (requires authentication)",
        mime_type="text/markdown",
    )
    async def user_watched_shows_resource() -> str:
        return await get_user_watched_shows()

    @mcp.resource(
        uri=MCP_RESOURCES["user_watched_movies"],
        name="user_watched_movies",
        description="Movies watched by the authenticated user from Trakt (requires authentication)",
        mime_type="text/markdown",
    )
    async def user_watched_movies_resource() -> str:
        return await get_user_watched_movies()
