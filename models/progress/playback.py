"""Playback progress models for the Trakt MCP server."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from models.types.ids import TraktIds


class PlaybackMovieInfo(BaseModel):
    """Movie information in playback progress."""

    title: str
    year: int | None = None
    ids: TraktIds = Field(default_factory=TraktIds)


class PlaybackEpisodeInfo(BaseModel):
    """Episode information in playback progress."""

    season: int
    number: int
    title: str | None = None
    ids: TraktIds = Field(default_factory=TraktIds)


class PlaybackShowInfo(BaseModel):
    """Show information in playback progress."""

    title: str
    year: int | None = None
    ids: TraktIds = Field(default_factory=TraktIds)


class PlaybackProgressResponse(BaseModel):
    """Playback progress response from Trakt API."""

    progress: float = Field(ge=0, le=100, description="Progress percentage 0-100")
    paused_at: datetime
    id: int
    type: Literal["movie", "episode"]
    movie: PlaybackMovieInfo | None = None
    episode: PlaybackEpisodeInfo | None = None
    show: PlaybackShowInfo | None = None
