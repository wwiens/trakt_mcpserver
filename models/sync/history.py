"""Sync history models for the Trakt MCP server."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class HistoryMovieInfo(BaseModel):
    """Movie information in history response."""

    title: str
    year: int | None = None
    ids: dict[str, str | int | None] = Field(default_factory=dict)


class HistoryShowInfo(BaseModel):
    """Show information in history response."""

    title: str
    year: int | None = None
    ids: dict[str, str | int | None] = Field(default_factory=dict)


class HistoryEpisodeInfo(BaseModel):
    """Episode information in history response."""

    season: int
    number: int
    title: str | None = None
    ids: dict[str, str | int | None] = Field(default_factory=dict)


class WatchHistoryItem(BaseModel):
    """Single watch history event from the API."""

    id: int = Field(description="Unique history event ID")
    watched_at: str = Field(description="ISO 8601 timestamp when watched")
    action: Literal["scrobble", "checkin", "watch"] = Field(
        description="How the watch was recorded"
    )
    type: Literal["movie", "episode"] = Field(description="Type of watched content")
    movie: HistoryMovieInfo | None = None
    episode: HistoryEpisodeInfo | None = None
    show: HistoryShowInfo | None = None


class TraktHistoryItem(BaseModel):
    """Item for history add/remove requests."""

    watched_at: datetime | None = Field(
        default=None, description="Timestamp when watched (UTC, ISO 8601)"
    )
    title: str | None = None
    year: int | None = Field(default=None, gt=1800)
    ids: dict[str, str | int | None] | None = None


class TraktHistoryRequest(BaseModel):
    """Request model for adding/removing history items."""

    movies: Annotated[list[TraktHistoryItem], Field(default_factory=list)]
    shows: Annotated[list[TraktHistoryItem], Field(default_factory=list)]
    seasons: Annotated[list[TraktHistoryItem], Field(default_factory=list)]
    episodes: Annotated[list[TraktHistoryItem], Field(default_factory=list)]


class HistorySummaryCount(BaseModel):
    """Summary counts for history add/remove operations."""

    movies: int = Field(default=0, ge=0)
    shows: int = Field(default=0, ge=0)
    seasons: int = Field(default=0, ge=0)
    episodes: int = Field(default=0, ge=0)


class HistoryNotFound(BaseModel):
    """Items not found during history add/remove operations."""

    movies: Annotated[list[TraktHistoryItem], Field(default_factory=list)]
    shows: Annotated[list[TraktHistoryItem], Field(default_factory=list)]
    seasons: Annotated[list[TraktHistoryItem], Field(default_factory=list)]
    episodes: Annotated[list[TraktHistoryItem], Field(default_factory=list)]


def _create_history_not_found() -> HistoryNotFound:
    """Factory function to create HistoryNotFound instance."""
    return HistoryNotFound(movies=[], shows=[], seasons=[], episodes=[])


class HistorySummary(BaseModel):
    """Add/remove history operation summary with counts and errors."""

    added: HistorySummaryCount | None = None
    deleted: HistorySummaryCount | None = None
    not_found: HistoryNotFound = Field(default_factory=_create_history_not_found)
