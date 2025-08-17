"""User tools for the Trakt MCP server."""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ValidationError

from client.user import UserClient
from config.auth import AUTH_VERIFICATION_URL
from config.mcp.tools import TOOL_NAMES
from models.formatters.user import UserFormatters
from server.base import BaseToolErrorMixin
from utils.api.error_types import AuthenticationRequiredError


class UserLimitParam(BaseModel):
    """Parameters for user data tools that support optional limiting."""

    limit: int = Field(
        0,
        ge=0,
        le=1000,
        description="Maximum number of items to return (0 for all)",
    )


async def fetch_user_watched_shows(limit: int = 0) -> str:
    """Fetch shows watched by the authenticated user from Trakt.

    Args:
        limit: Maximum number of shows to return (0 for all)

    Returns:
        Information about user's watched shows
    """
    # Validate parameters with Pydantic for normalization and constraints
    try:
        params = UserLimitParam(limit=limit)
        limit = params.limit
    except ValidationError as e:
        # Extract structured validation details for the error mixin
        validation_errors: list[dict[str, Any]] = [
            {
                "field": str(error.get("loc", ["limit"])[-1]),
                "message": str(error.get("msg", "Invalid value")),
                "type": str(error.get("type", "validation_error")),
                "input": error.get("input"),
            }
            for error in e.errors()
        ]

        # Create summary message for human readability
        field_messages = [
            f"{err['field']}: {err['message']}" for err in validation_errors
        ]
        summary_message = (
            f"Invalid parameters for user watched shows: {'; '.join(field_messages)}"
        )

        # Use project's error mixin to attach structured details and request context
        raise BaseToolErrorMixin.handle_validation_error(
            summary_message,
            validation_errors=validation_errors,
            operation="fetch_user_watched_shows_validation",
        ) from e

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
    # Validate parameters with Pydantic for normalization and constraints
    try:
        params = UserLimitParam(limit=limit)
        limit = params.limit
    except ValidationError as e:
        # Extract structured validation details for the error mixin
        validation_errors: list[dict[str, Any]] = [
            {
                "field": str(error.get("loc", ["limit"])[-1]),
                "message": str(error.get("msg", "Invalid value")),
                "type": str(error.get("type", "validation_error")),
                "input": error.get("input"),
            }
            for error in e.errors()
        ]

        # Create summary message for human readability
        field_messages = [
            f"{err['field']}: {err['message']}" for err in validation_errors
        ]
        summary_message = (
            f"Invalid parameters for user watched movies: {'; '.join(field_messages)}"
        )

        # Use project's error mixin to attach structured details and request context
        raise BaseToolErrorMixin.handle_validation_error(
            summary_message,
            validation_errors=validation_errors,
            operation="fetch_user_watched_movies_validation",
        ) from e

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
