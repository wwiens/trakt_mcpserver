"""Progress-specific MCP tool name definitions."""

from typing import Final

PROGRESS_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_show_progress",
        "fetch_playback_progress",
        "remove_playback_item",
    }
)

__all__ = ["PROGRESS_TOOLS"]
