"""Progress models for the Trakt MCP server."""

from .playback import (
    PlaybackEpisodeInfo,
    PlaybackMovieInfo,
    PlaybackProgressResponse,
    PlaybackShowInfo,
)
from .show_progress import (
    EpisodeInfo,
    EpisodeProgressResponse,
    HiddenSeasonResponse,
    SeasonProgressResponse,
    ShowProgressResponse,
)

__all__ = [
    "EpisodeInfo",
    "EpisodeProgressResponse",
    "HiddenSeasonResponse",
    "PlaybackEpisodeInfo",
    "PlaybackMovieInfo",
    "PlaybackProgressResponse",
    "PlaybackShowInfo",
    "SeasonProgressResponse",
    "ShowProgressResponse",
]
