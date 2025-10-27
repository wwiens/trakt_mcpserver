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

# Type alias for search tool handlers
ToolHandler = Callable[[str, int, int | None], Awaitable[str]]


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
    page: int | None = Field(
        default=None,
        ge=1,
        description="Page number for pagination (optional). If not provided, returns all results.",
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


def _validate_search_params(
    query: str, limit: int, page: int | None, operation: str
) -> tuple[str, int, int | None]:
    """Normalize and validate search parameters, mapping Pydantic errors to MCP."""
    try:
        params = QueryParam(query=query, limit=limit, page=page)
    except ValidationError as e:
        validation_errors: list[dict[str, Any]] = [
            {
                "field": str(err.get("loc", ["query"])[-1]),
                "message": str(err.get("msg", "Invalid value")),
                "type": str(err.get("type", "validation_error")),
                "input": repr(err.get("input")),
            }
            for err in e.errors()
        ]
        summary = "Invalid parameters for search: " + "; ".join(
            f"{ve['field']}: {ve['message']}" for ve in validation_errors
        )
        raise BaseToolErrorMixin.handle_validation_error(
            summary, validation_errors=validation_errors, operation=operation
        ) from e
    else:
        return params.query, params.limit, params.page


@handle_api_errors_func
async def search_shows(
    query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Search for shows on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return per page
        page: Page number (optional). If not provided, returns all results.

    Returns:
        Formatted search results

    Raises:
        InvalidParamsError: If query and limit are invalid
        InternalError: If an error occurs during search
    """
    query, limit, page = _validate_search_params(
        query, limit, page, operation="search_shows_validation"
    )

    client = SearchClient()

    try:
        # Perform the search
        results = await client.search_shows(query, limit, page)

        # Format and return the results
        return SearchFormatters.format_show_search_results(results)
    except MCPError:
        raise
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="search shows", error=e, query=query, limit=limit, page=page
        ) from e


@handle_api_errors_func
async def search_movies(
    query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Search for movies on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return per page
        page: Page number (optional). If not provided, returns all results.

    Returns:
        Formatted search results

    Raises:
        InvalidParamsError: If query and limit are invalid
        InternalError: If an error occurs during search
    """
    query, limit, page = _validate_search_params(
        query, limit, page, operation="search_movies_validation"
    )

    client = SearchClient()

    try:
        results = await client.search_movies(query, limit, page)
        return SearchFormatters.format_movie_search_results(results)
    except MCPError:
        raise
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="search movies", error=e, query=query, limit=limit, page=page
        ) from e


def register_search_tools(
    mcp: FastMCP,
) -> tuple[ToolHandler, ToolHandler]:
    """Register search tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["search_shows"],
        description="Search for TV shows on Trakt by title",
    )
    async def search_shows_tool(
        query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> str:
        return await search_shows(query, limit, page)

    @mcp.tool(
        name=TOOL_NAMES["search_movies"],
        description="Search for movies on Trakt by title",
    )
    async def search_movies_tool(
        query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> str:
        return await search_movies(query, limit, page)

    # Return handlers for type checker visibility
    return (search_shows_tool, search_movies_tool)
