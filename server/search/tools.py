# pyright: reportUnusedFunction=none
"""Search tools for the Trakt MCP server."""

from mcp.server.fastmcp import FastMCP

from client.search import SearchClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.search import SearchFormatters
from utils.validation import validate_limit, validate_non_empty_string


async def search_shows(query: str, limit: int = DEFAULT_LIMIT) -> str:
    """Search for shows on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted search results
    """
    # Validate inputs
    validate_non_empty_string(query, "query")
    validate_limit(limit)

    client = SearchClient()

    # Perform the search
    results = await client.search_shows(query, limit)

    # Format and return the results
    return SearchFormatters.format_show_search_results(results)


async def search_movies(query: str, limit: int = DEFAULT_LIMIT) -> str:
    """Search for movies on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted search results
    """
    # Validate inputs
    validate_non_empty_string(query, "query")
    validate_limit(limit)

    client = SearchClient()
    results = await client.search_movies(query, limit)
    return SearchFormatters.format_movie_search_results(results)


def register_search_tools(mcp: FastMCP) -> None:
    """Register search tools with the MCP server."""

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
