"""User tools for the Trakt MCP server."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from client.user import UserClient
from config.auth import AUTH_VERIFICATION_URL
from config.mcp.tools import TOOL_NAMES
from models.formatters.user import UserFormatters
from utils.api.error_types import AuthenticationRequiredError

# Import start_device_auth from auth module


async def fetch_user_watched_shows(limit: int = 0) -> str:
    """Fetch shows watched by the authenticated user from Trakt.

    Args:
        limit: Maximum number of shows to return (0 for all)

    Returns:
        Information about user's watched shows
    """
    client = UserClient()

    if not client.is_authenticated():
        raise AuthenticationRequiredError(
            action="access your watched shows",
            auth_url=AUTH_VERIFICATION_URL,
            message="Authentication required to access your watched shows from Trakt",
        )

    shows = await client.get_user_watched_shows()

    # Apply limit if requested
    if limit > 0 and len(shows) > limit:
        shows = shows[:limit]

    return UserFormatters.format_user_watched_shows(shows)


async def fetch_user_watched_movies(limit: int = 0) -> str:
    """Fetch movies watched by the authenticated user from Trakt.

    Args:
        limit: Maximum number of movies to return (0 for all)

    Returns:
        Information about user's watched movies
    """
    client = UserClient()

    if not client.is_authenticated():
        raise AuthenticationRequiredError(
            action="access your watched movies",
            auth_url=AUTH_VERIFICATION_URL,
            message="Authentication required to access your watched movies from Trakt",
        )

    movies = await client.get_user_watched_movies()

    # Apply limit if requested
    if limit > 0 and len(movies) > limit:
        movies = movies[:limit]

    return UserFormatters.format_user_watched_movies(movies)


def register_user_tools(mcp: FastMCP) -> tuple[Any, Any]:
    """Register user tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_user_watched_shows"],
        description="Fetch TV shows watched by the authenticated user from Trakt",
    )
    async def fetch_user_watched_shows_tool(limit: int = 0) -> str:
        return await fetch_user_watched_shows(limit)

    @mcp.tool(
        name=TOOL_NAMES["fetch_user_watched_movies"],
        description="Fetch movies watched by the authenticated user from Trakt",
    )
    async def fetch_user_watched_movies_tool(limit: int = 0) -> str:
        return await fetch_user_watched_movies(limit)

    # Return handlers for type checker visibility
    return (fetch_user_watched_shows_tool, fetch_user_watched_movies_tool)
