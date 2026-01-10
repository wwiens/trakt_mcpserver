"""Search tools for the Trakt MCP server."""

from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field, ValidationError, field_validator

from client.search.client import SearchClient
from config.api import DEFAULT_LIMIT
from config.mcp.descriptions import (
    PAGE_DESCRIPTION,
    SEARCH_LIMIT_DESCRIPTION,
    SEARCH_QUERY_DESCRIPTION,
)
from config.mcp.tools import TOOL_NAMES
from models.formatters.search import SearchFormatters
from server.base import BaseToolErrorMixin, LimitPageValidatorMixin
from utils.api.errors import MCPError, handle_api_errors_func

# Type alias for search tool handlers
ToolHandler = Callable[[str, int, int | None], Awaitable[str]]


class QueryParam(LimitPageValidatorMixin):
    """Parameters for tools that require a search query and result limit."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description=SEARCH_QUERY_DESCRIPTION,
    )
    limit: int = Field(
        DEFAULT_LIMIT,
        ge=0,
        le=100,
        description="Maximum results to return (0=all up to 100, default=10)",
    )
    page: int | None = Field(
        default=None,
        ge=1,
        description="Page number for pagination (optional). If not provided, auto-paginates.",
    )

    @field_validator("query", mode="before")
    @classmethod
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
                "field": str(err.get("loc", ())[-1]) if err.get("loc") else "value",
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


async def _run_search(
    op: str,
    fetch: Callable[..., Awaitable[Any]],
    fmt: Callable[[Any], str],
    query: str,
    limit: int,
    page: int | None,
) -> str:
    """Run a search operation with validation, fetch, and formatting.

    Args:
        op: Operation name for error handling
        fetch: Client method to fetch results (accepts query, limit, page)
        fmt: Formatter function to format results
        query: Search query string
        limit: Maximum number of results to return
        page: Page number (optional)

    Returns:
        Formatted search results

    Raises:
        MCPError: If validation or API errors occur
    """
    q, lim, p = _validate_search_params(
        query, limit, page, operation=f"{op}_validation"
    )
    try:
        results = await fetch(q, lim, p)
        return fmt(results)
    except MCPError:
        raise
    except Exception as e:
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation=op, error=e, query=q, limit=lim, page=p
        ) from e


@handle_api_errors_func
async def search_shows(
    query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Search for shows on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum results to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        page: Page number (optional). If not provided, auto-paginates.

    Returns:
        Formatted search results

    Raises:
        InvalidParamsError: If query and limit are invalid
        InternalError: If an error occurs during search
    """
    client = SearchClient()
    return await _run_search(
        op="search shows",
        fetch=client.search_shows,
        fmt=SearchFormatters.format_show_search_results,
        query=query,
        limit=limit,
        page=page,
    )


@handle_api_errors_func
async def search_movies(
    query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Search for movies on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum results to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        page: Page number (optional). If not provided, auto-paginates.

    Returns:
        Formatted search results

    Raises:
        InvalidParamsError: If query and limit are invalid
        InternalError: If an error occurs during search
    """
    client = SearchClient()
    return await _run_search(
        op="search movies",
        fetch=client.search_movies,
        fmt=SearchFormatters.format_movie_search_results,
        query=query,
        limit=limit,
        page=page,
    )


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
        query: Annotated[
            str, Field(min_length=1, description=SEARCH_QUERY_DESCRIPTION)
        ],
        limit: Annotated[
            int, Field(description=SEARCH_LIMIT_DESCRIPTION)
        ] = DEFAULT_LIMIT,
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await search_shows(query, limit, page)

    @mcp.tool(
        name=TOOL_NAMES["search_movies"],
        description="Search for movies on Trakt by title",
    )
    async def search_movies_tool(
        query: Annotated[
            str, Field(min_length=1, description=SEARCH_QUERY_DESCRIPTION)
        ],
        limit: Annotated[
            int, Field(description=SEARCH_LIMIT_DESCRIPTION)
        ] = DEFAULT_LIMIT,
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await search_movies(query, limit, page)

    # Return handlers for type checker visibility
    return (search_shows_tool, search_movies_tool)
