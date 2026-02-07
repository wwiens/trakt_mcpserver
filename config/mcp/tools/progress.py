"""Progress-specific MCP tool name definitions."""

from collections.abc import Mapping
from typing import Final

PROGRESS_TOOLS: Final[Mapping[str, str]] = {
    "fetch_show_progress": "fetch_show_progress",
    "fetch_playback_progress": "fetch_playback_progress",
    "remove_playback_item": "remove_playback_item",
}

__all__ = ["PROGRESS_TOOLS"]
