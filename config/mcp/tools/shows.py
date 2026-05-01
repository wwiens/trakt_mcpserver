"""Show-specific MCP tool name definitions."""

from typing import Final

SHOW_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_trending_shows",
        "fetch_popular_shows",
        "fetch_favorited_shows",
        "fetch_played_shows",
        "fetch_watched_shows",
        "fetch_anticipated_shows",
        "fetch_show_ratings",
        "fetch_show_summary",
        "fetch_show_videos",
        "fetch_related_shows",
        "fetch_show_seasons",
        "fetch_show_people",
    }
)
