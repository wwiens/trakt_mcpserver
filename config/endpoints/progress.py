"""Progress endpoints for the Trakt MCP server."""

from collections.abc import Mapping
from typing import Final

PROGRESS_ENDPOINTS: Final[Mapping[str, str]] = {
    "show_progress_watched": "/shows/:id/progress/watched",
    "sync_playback": "/sync/playback",
    "sync_playback_type": "/sync/playback/:type",
    "sync_playback_remove": "/sync/playback/:id",
}
