"""
Basic prompts for Trakt MCP server.

This module provides fundamental conversation prompts for entertainment
discovery and search scenarios.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP


async def discover_trending() -> list[dict[str, Any]]:
    """Prompt for discovering trending entertainment content."""
    return [
        {
            "role": "user",
            "content": "Show me what movies and TV shows are trending on Trakt right now. Please include both movies and shows, and provide details about ratings, genres, and why they're popular.",
        }
    ]


async def search_entertainment() -> list[dict[str, Any]]:
    """Prompt for searching entertainment content."""
    return [
        {
            "role": "user",
            "content": "Help me search for a movie or TV show. I'd like to find something specific by title, and also get recommendations based on what I'm looking for. What would you like to find?",
        }
    ]


def register_basic_prompts(mcp: FastMCP) -> tuple[Any, Any]:
    """Register basic prompts with the MCP server.

    Args:
        mcp: The FastMCP server instance to register prompts with

    Returns:
        Tuple of registered prompt handlers (for type checker visibility)
    """

    @mcp.prompt(
        name="discover_trending",
        description="Discover trending movies and TV shows on Trakt",
    )
    async def discover_trending_prompt() -> list[dict[str, Any]]:
        """Wrapper for discover_trending prompt."""
        return await discover_trending()

    @mcp.prompt(
        name="search_entertainment",
        description="Search for movies or TV shows by title with personalized recommendations",
    )
    async def search_entertainment_prompt() -> list[dict[str, Any]]:
        """Wrapper for search_entertainment prompt."""
        return await search_entertainment()

    # Return handlers to satisfy type checker
    return (discover_trending_prompt, search_entertainment_prompt)
