"""Search tools for the Trakt MCP server."""

from collections.abc import Awaitable, Callable
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, PositiveInt, ValidationError, field_validator

from client.search.client import SearchClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.search import SearchFormatters
from server.base import BaseToolErrorMixin
from utils.api.errors import MCPError, handle_api_errors_func


class QueryParam(BaseModel):
    """Parameters for tools that require a search query and result limit."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Non-empty, non-whitespace search query",
    )
    limit: PositiveInt = Field(
        DEFAULT_LIMIT,
        le=1000,
        description="Maximum number of search results to return (1-1000)",
    )

    @field_validator("query", mode="before")
    def _validate_query(cls, v: object) -> object:
        if isinstance(v, str):
            # Strip whitespace and check if result is empty
            stripped = v.strip()
            if not stripped:
                raise ValueError(
                    "Search query cannot be empty or contain only whitespace"
                )
            return stripped
        return v


@handle_api_errors_func
async def search_shows(query: str, limit: int = DEFAULT_LIMIT) -> str:
    """Search for shows on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted search results

    Raises:
        InvalidParamsError: If query and limit are invalid
        InternalError: If an error occurs during search
    """
    # Validate parameters with Pydantic for normalization and constraints
    try:
        params = QueryParam(query=query, limit=limit)
        query, limit = params.query, params.limit
    except ValidationError as e:
        # Extract structured validation details for the error mixin
        validation_errors: list[dict[str, Any]] = [
            {
                "field": str(error.get("loc", ["query"])[-1]),
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
        summary_message = f"Invalid parameters for search: {'; '.join(field_messages)}"

        # Use project's error mixin to attach structured details and request context
        raise BaseToolErrorMixin.handle_validation_error(
            summary_message,
            validation_errors=validation_errors,
            operation="search_shows_validation",
        ) from e

    client = SearchClient()

    try:
        # Perform the search
        results = await client.search_shows(query, params.limit)

        # Format and return the results
        return SearchFormatters.format_show_search_results(results)
    except MCPError:
        raise
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="search shows", error=e, query=query, limit=params.limit
        ) from e


@handle_api_errors_func
async def search_movies(query: str, limit: int = DEFAULT_LIMIT) -> str:
    """Search for movies on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted search results

    Raises:
        InvalidParamsError: If query and limit are invalid
        InternalError: If an error occurs during search
    """
    # Validate parameters with Pydantic for normalization and constraints
    try:
        params = QueryParam(query=query, limit=limit)
        query, limit = params.query, params.limit
    except ValidationError as e:
        # Extract structured validation details for the error mixin
        validation_errors: list[dict[str, Any]] = [
            {
                "field": str(error.get("loc", ["query"])[-1]),
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
        summary_message = f"Invalid parameters for search: {'; '.join(field_messages)}"

        # Use project's error mixin to attach structured details and request context
        raise BaseToolErrorMixin.handle_validation_error(
            summary_message,
            validation_errors=validation_errors,
            operation="search_movies_validation",
        ) from e

    client = SearchClient()

    try:
        results = await client.search_movies(query, params.limit)
        return SearchFormatters.format_movie_search_results(results)
    except MCPError:
        raise
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="search movies", error=e, query=query, limit=params.limit
        ) from e


def register_search_tools(
    mcp: FastMCP,
) -> tuple[Callable[..., Awaitable[str]], Callable[..., Awaitable[str]]]:
    """Register search tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["search_shows"],
        description="Search for TV shows on Trakt by title",
    )
    async def search_shows_tool(query: str, limit: int = DEFAULT_LIMIT) -> str:
        return await search_shows(query, limit)

    @mcp.tool(
        name=TOOL_NAMES["search_movies"],
        description="Search for movies on Trakt by title",
    )
    async def search_movies_tool(query: str, limit: int = DEFAULT_LIMIT) -> str:
        return await search_movies(query, limit)

    # Return handlers for type checker visibility
    return (search_shows_tool, search_movies_tool)
