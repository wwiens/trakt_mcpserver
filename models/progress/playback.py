"""Playback progress models for the Trakt MCP server."""

from typing import Literal

from pydantic import BaseModel, Field


class PlaybackMovieInfo(BaseModel):
    """Movie information in playback progress."""

    title: str
    year: int | None = None
    ids: dict[str, str | int | dict[str, str] | None] = Field(default_factory=dict)


class PlaybackEpisodeInfo(BaseModel):
    """Episode information in playback progress."""

    season: int
    number: int
    title: str | None = None
    ids: dict[str, str | int | dict[str, str] | None] = Field(default_factory=dict)


class PlaybackShowInfo(BaseModel):
    """Show information in playback progress."""

    title: str
    year: int | None = None
    ids: dict[str, str | int | dict[str, str] | None] = Field(default_factory=dict)


class PlaybackProgressResponse(BaseModel):
    """Playback progress response from Trakt API."""

    progress: float = Field(ge=0, le=100, description="Progress percentage 0-100")
    paused_at: str
    id: int
    type: Literal["movie", "episode"]
    movie: PlaybackMovieInfo | None = None
    episode: PlaybackEpisodeInfo | None = None
    show: PlaybackShowInfo | None = None
