"""Recommendation MCP tool name definitions."""

from typing import Final

RECOMMENDATIONS_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_movie_recommendations",
        "fetch_show_recommendations",
        "hide_movie_recommendation",
        "hide_show_recommendation",
        "unhide_movie_recommendation",
        "unhide_show_recommendation",
    }
)
