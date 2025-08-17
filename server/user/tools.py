"""User tools for the Trakt MCP server."""

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ValidationError

from client.user.client import UserClient
from config.auth import AUTH_VERIFICATION_URL
from config.mcp.tools import TOOL_NAMES
from models.formatters.user import UserFormatters
from server.base import BaseToolErrorMixin
from utils.api.error_types import AuthenticationRequiredError

# Type aliases for user tools
T = TypeVar("T")
Fetcher = Callable[[], Awaitable[list[T]]]
Formatter = Callable[[list[T]], str]
ToolHandler = Callable[[int | None], Awaitable[str]]


def _validate_and_normalize_limit(value: int | None, *, operation: str) -> int:
    # Handle None as 0 (return all items) for MCP bridge compatibility
    if value is None:
        value = 0

    try:
        params = UserLimitParam(limit=value)
        return params.limit
    except ValidationError as e:
        validation_errors: list[dict[str, Any]] = [
            {
                "field": str(error.get("loc", ["limit"])[-1]),
                "message": str(error.get("msg", "Invalid value")),
                "type": str(error.get("type", "validation_error")),
                "input": error.get("input"),
            }
            for error in e.errors()
        ]
        field_messages = [
            f"{err['field']}: {err['message']}" for err in validation_errors
        ]
        summary_message = (
            f"Invalid parameters for {operation.replace('_', ' ')}: "
            + "; ".join(field_messages)
        )
        raise BaseToolErrorMixin.handle_validation_error(
            summary_message,
            validation_errors=validation_errors,
            operation=f"{operation}_validation",
        ) from e


async def _fetch_user_items(
    *,
    limit: int | None,
    operation: str,
    on_auth_action: str,
    fetcher: Fetcher[T],
    formatter: Formatter[T],
) -> str:
    """Common helper for fetching and formatting user data with auth checks.

    Args:
        limit: Maximum number of items to return (0 for all)
        operation: Operation name for validation errors
        on_auth_action: Human-readable action for auth error messages
        fetcher: Async function that fetches the data
        formatter: Function that formats the data to string

    Returns:
        Formatted string of user data

    Raises:
        AuthenticationRequiredError: If user is not authenticated
        BaseToolError: If validation fails
    """
    limit = _validate_and_normalize_limit(limit, operation=operation)
    client = UserClient()
    if not client.is_authenticated():
        raise AuthenticationRequiredError(
            action=on_auth_action,
            auth_url=AUTH_VERIFICATION_URL,
            message=f"Authentication required to {on_auth_action} from Trakt",
        )
    items = await fetcher()
    return formatter(items[:limit] if limit > 0 else items)


class UserLimitParam(BaseModel):
    """Parameters for user data tools that support optional limiting."""

    limit: int = Field(
        0,
        ge=0,
        le=1000,
        description="Maximum number of items to return (0 for all)",
    )


async def fetch_user_watched_shows(limit: int | None = 0) -> str:
    """Fetch shows watched by the authenticated user from Trakt.

    Args:
        limit: Maximum number of shows to return (0 for all)

    Returns:
        Information about user's watched shows
    """
    return await _fetch_user_items(
        limit=limit,
        operation="fetch_user_watched_shows",
        on_auth_action="access your watched shows",
        fetcher=UserClient().get_user_watched_shows,
        formatter=UserFormatters.format_user_watched_shows,
    )


async def fetch_user_watched_movies(limit: int | None = 0) -> str:
    """Fetch movies watched by the authenticated user from Trakt.

    Args:
        limit: Maximum number of movies to return (0 for all)

    Returns:
        Information about user's watched movies
    """
    return await _fetch_user_items(
        limit=limit,
        operation="fetch_user_watched_movies",
        on_auth_action="access your watched movies",
        fetcher=UserClient().get_user_watched_movies,
        formatter=UserFormatters.format_user_watched_movies,
    )


def register_user_tools(mcp: FastMCP) -> tuple[ToolHandler, ToolHandler]:
    """Register user tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_user_watched_shows"],
        description="Fetch TV shows watched by the authenticated user from Trakt",
    )
    @BaseToolErrorMixin.with_error_handling(
        operation="fetch_user_watched_shows_tool",
        tool=TOOL_NAMES["fetch_user_watched_shows"],
    )
    async def fetch_user_watched_shows_tool(limit: int | None = 0) -> str:
        return await fetch_user_watched_shows(limit)

    @mcp.tool(
        name=TOOL_NAMES["fetch_user_watched_movies"],
        description="Fetch movies watched by the authenticated user from Trakt",
    )
    @BaseToolErrorMixin.with_error_handling(
        operation="fetch_user_watched_movies_tool",
        tool=TOOL_NAMES["fetch_user_watched_movies"],
    )
    async def fetch_user_watched_movies_tool(limit: int | None = 0) -> str:
        return await fetch_user_watched_movies(limit)

    # Return handlers for type checker visibility
    return (fetch_user_watched_shows_tool, fetch_user_watched_movies_tool)
