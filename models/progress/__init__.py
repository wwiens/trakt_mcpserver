"""Progress models for the Trakt MCP server."""

from typing import Final

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

__all__: Final[list[str]] = [
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
