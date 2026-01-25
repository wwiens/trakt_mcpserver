"""Playback progress models for the Trakt MCP server."""

from typing import Literal, NotRequired, TypedDict


class PlaybackMovieInfo(TypedDict):
    """Movie information in playback progress."""

    title: str
    year: int | None
    ids: dict[str, str | int | None]


class PlaybackEpisodeInfo(TypedDict):
    """Episode information in playback progress."""

    season: int
    number: int
    title: str | None
    ids: dict[str, str | int | None]


class PlaybackShowInfo(TypedDict):
    """Show information in playback progress."""

    title: str
    year: int | None
    ids: dict[str, str | int | None]


class PlaybackProgressResponse(TypedDict):
    """Playback progress response from Trakt API."""

    progress: float  # 0-100 percentage
    paused_at: str
    id: int
    type: Literal["movie", "episode"]
    movie: NotRequired[PlaybackMovieInfo]
    episode: NotRequired[PlaybackEpisodeInfo]
    show: NotRequired[PlaybackShowInfo]
