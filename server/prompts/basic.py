"""
Basic prompts for Trakt MCP server.

This module provides fundamental conversation prompts for entertainment
discovery and search scenarios.
"""

from fastmcp import FastMCP
from fastmcp.prompts import Message


_DISCOVER_TRENDING_TEXT = (
    "Show me what movies and TV shows are trending on Trakt right now. "
    "Please include both movies and shows, and provide details about "
    "ratings, genres, and why they're popular."
)

_SEARCH_ENTERTAINMENT_TEXT = (
    "Help me search for a movie or TV show. I'd like to find something "
    "specific by title, and also get recommendations based on what I'm "
    "looking for. What would you like to find?"
)


async def discover_trending() -> list[Message]:
    """Prompt for discovering trending entertainment content."""
    return [Message(_DISCOVER_TRENDING_TEXT)]


async def search_entertainment() -> list[Message]:
    """Prompt for searching entertainment content."""
    return [Message(_SEARCH_ENTERTAINMENT_TEXT)]


def register_basic_prompts(mcp: FastMCP) -> tuple[object, object]:
    """Register basic prompts with the MCP server."""

    @mcp.prompt(
        name="discover_trending",
        description="Discover trending movies and TV shows on Trakt",
    )
    async def discover_trending_prompt() -> list[Message]:
        return await discover_trending()

    @mcp.prompt(
        name="search_entertainment",
        description=(
            "Search for movies or TV shows by title with personalized recommendations"
        ),
    )
    async def search_entertainment_prompt() -> list[Message]:
        return await search_entertainment()

    return (discover_trending_prompt, search_entertainment_prompt)
