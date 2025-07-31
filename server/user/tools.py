# pyright: reportUnusedFunction=none
"""User tools for the Trakt MCP server."""

from mcp.server.fastmcp import FastMCP

from client.user import UserClient
from config.mcp.tools import TOOL_NAMES
from models.formatters.user import UserFormatters
from utils.api.errors import InvalidParamsError, InvalidRequestError
from utils.validation import validate_limit

# Import start_device_auth from auth module
from ..auth.tools import start_device_auth


async def fetch_user_watched_shows(limit: int = 0) -> str:
    """Fetch shows watched by the authenticated user from Trakt.

    Args:
        limit: Maximum number of shows to return (0 for all)

    Returns:
        Information about user's watched shows
    """
    # Validate inputs
    validate_limit(limit)

    client = UserClient()

    try:
        shows = await client.get_user_watched_shows()
    except InvalidParamsError:
        # Client-side parameter validation error
        auth_instructions = await start_device_auth()
        return f"""Authentication required to access your watched shows.

{auth_instructions}

After you've completed the authorization process on the Trakt website, please tell me "I've completed the authorization" so I can check if it was successful and retrieve your watched shows."""
    except InvalidRequestError as e:
        # Check if this is an auth-related error (401 Unauthorized)
        if e.data and e.data.get("http_status") == 401:
            # Start the auth flow automatically for auth errors
            auth_instructions = await start_device_auth()
            return f"""Authentication required to access your watched shows.

{auth_instructions}

After you've completed the authorization process on the Trakt website, please tell me "I've completed the authorization" so I can check if it was successful and retrieve your watched shows."""
        else:
            # Re-raise non-auth InvalidRequestError (rate limit, etc.)
            raise

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
    # Validate inputs
    validate_limit(limit)

    client = UserClient()

    try:
        movies = await client.get_user_watched_movies()
    except InvalidParamsError:
        # Client-side parameter validation error
        auth_instructions = await start_device_auth()
        return f"""Authentication required to access your watched movies.

{auth_instructions}

After you've completed the authorization process on the Trakt website, please tell me "I've completed the authorization" so I can check if it was successful and retrieve your watched movies."""
    except InvalidRequestError as e:
        # Check if this is an auth-related error (401 Unauthorized)
        if e.data and e.data.get("http_status") == 401:
            # Start the auth flow automatically for auth errors
            auth_instructions = await start_device_auth()
            return f"""Authentication required to access your watched movies.

{auth_instructions}

After you've completed the authorization process on the Trakt website, please tell me "I've completed the authorization" so I can check if it was successful and retrieve your watched movies."""
        else:
            # Re-raise non-auth InvalidRequestError (rate limit, etc.)
            raise

    # Apply limit if requested
    if limit > 0 and len(movies) > limit:
        movies = movies[:limit]

    return UserFormatters.format_user_watched_movies(movies)


def register_user_tools(mcp: FastMCP) -> None:
    """Register user tools with the MCP server."""

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
