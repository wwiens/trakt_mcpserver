"""Season-specific MCP tool name definitions."""

from typing import Final

SEASON_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_season_info",
        "fetch_season_episodes",
        "fetch_season_ratings",
        "fetch_season_stats",
        "fetch_season_people",
        "fetch_season_videos",
        "fetch_season_watching",
        "fetch_season_translations",
        "fetch_season_lists",
    }
)
