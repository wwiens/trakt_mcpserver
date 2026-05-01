"""Episode-specific MCP tool name definitions."""

from typing import Final

EPISODE_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_episode_summary",
        "fetch_episode_translations",
        "fetch_episode_lists",
        "fetch_episode_people",
        "fetch_episode_ratings",
        "fetch_episode_stats",
        "fetch_episode_watching",
        "fetch_episode_videos",
    }
)
