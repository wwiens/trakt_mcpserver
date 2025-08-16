"""Search tools for the Trakt MCP server."""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from client.search.client import SearchClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.search import SearchFormatters
from server.base import BaseToolErrorMixin
from utils.api.errors import MCPError


class QueryParam(BaseModel):
    """Parameters for tools that require a search query."""

    query: str = Field(..., min_length=1, description="Non-empty search query")


async def search_shows(query: str, limit: int = DEFAULT_LIMIT) -> str:
    """Search for shows on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted search results

    Raises:
        InvalidParamsError: If query is invalid
        InternalError: If an error occurs during search
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = QueryParam(query=query)
    query = params.query

    client = SearchClient()

    try:
        # Perform the search
        results = await client.search_shows(query, limit)

        # Format and return the results
        return SearchFormatters.format_show_search_results(results)
    except MCPError:
        raise
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="search shows", error=e, query=query, limit=limit
        ) from e


async def search_movies(query: str, limit: int = DEFAULT_LIMIT) -> str:
    """Search for movies on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted search results

    Raises:
        InvalidParamsError: If query is invalid
        InternalError: If an error occurs during search
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = QueryParam(query=query)
    query = params.query

    client = SearchClient()

    try:
        results = await client.search_movies(query, limit)
        return SearchFormatters.format_movie_search_results(results)
    except MCPError:
        raise
    except Exception as e:
        # Convert any unexpected errors to structured MCP errors
        raise BaseToolErrorMixin.handle_unexpected_error(
            operation="search movies", error=e, query=query, limit=limit
        ) from e


def register_search_tools(mcp: FastMCP) -> tuple[Any, Any]:
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
