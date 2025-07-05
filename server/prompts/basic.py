"""
Basic prompts for Trakt MCP server.

This module provides fundamental conversation prompts for entertainment
discovery and search scenarios.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP


def register_basic_prompts(mcp: FastMCP) -> None:
    """Register basic prompts with the MCP server.

    Args:
        mcp: The FastMCP server instance to register prompts with
    """

    @mcp.prompt(
        name="discover_trending",
        description="Discover trending movies and TV shows on Trakt",
    )
    async def discover_trending() -> list[dict[str, Any]]:  # type: ignore[reportUnusedFunction]
        """Prompt for discovering trending entertainment content."""
        return [
            {
                "role": "user",
                "content": "Show me what movies and TV shows are trending on Trakt right now. Please include both movies and shows, and provide details about ratings, genres, and why they're popular.",
            }
        ]

    @mcp.prompt(
        name="search_entertainment",
        description="Search for movies or TV shows by title with personalized recommendations",
    )
    async def search_entertainment() -> list[dict[str, Any]]:  # type: ignore[reportUnusedFunction]
        """Prompt for searching entertainment content."""
        return [
            {
                "role": "user",
                "content": "Help me search for a movie or TV show. I'd like to find something specific by title, and also get recommendations based on what I'm looking for. What would you like to find?",
            }
        ]
