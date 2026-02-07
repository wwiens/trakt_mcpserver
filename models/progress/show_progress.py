"""Show progress models for the Trakt MCP server."""

from typing import Annotated

from pydantic import BaseModel, Field

from models.types.ids import TraktIds


class EpisodeProgressResponse(BaseModel):
    """Episode progress response from Trakt API."""

    number: int
    completed: bool
    last_watched_at: str | None = None


class SeasonProgressResponse(BaseModel):
    """Season progress response from Trakt API."""

    number: int
    title: str | None = None
    aired: int
    completed: int
    episodes: Annotated[list[EpisodeProgressResponse], Field(default_factory=list)]


class HiddenSeasonResponse(BaseModel):
    """Hidden season response from Trakt API."""

    number: int
    ids: TraktIds = Field(default_factory=TraktIds)


class EpisodeInfo(BaseModel):
    """Episode information for next/last episode."""

    season: int
    number: int
    title: str | None = None
    ids: TraktIds = Field(default_factory=TraktIds)


class ShowProgressResponse(BaseModel):
    """Show watched progress response from Trakt API."""

    aired: int
    completed: int
    last_watched_at: str | None = None
    reset_at: str | None = None
    seasons: Annotated[list[SeasonProgressResponse], Field(default_factory=list)]
    hidden_seasons: Annotated[list[HiddenSeasonResponse], Field(default_factory=list)]
    next_episode: EpisodeInfo | None = None
    last_episode: EpisodeInfo | None = None
