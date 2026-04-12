"""Sync history models for the Trakt MCP server."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from models.types.ids import TraktIds


class HistoryMovieInfo(BaseModel):
    """Movie information in history response."""

    title: str
    year: int | None = None
    ids: TraktIds = Field(default_factory=TraktIds)


class HistoryShowInfo(BaseModel):
    """Show information in history response."""

    title: str
    year: int | None = None
    ids: TraktIds = Field(default_factory=TraktIds)


class HistoryEpisodeInfo(BaseModel):
    """Episode information in history response."""

    season: int
    number: int
    title: str | None = None
    ids: TraktIds = Field(default_factory=TraktIds)


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
    year: int | None = Field(default=None, ge=1800)
    ids: TraktIds | None = None


class TraktHistoryRequest(BaseModel):
    """Request model for adding/removing history items."""

    movies: list[TraktHistoryItem] | None = None
    shows: list[TraktHistoryItem] | None = None
    seasons: list[TraktHistoryItem] | None = None
    episodes: list[TraktHistoryItem] | None = None


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


class HistoryQueryParams(BaseModel):
    """Parameters for history query filtering with validation."""

    history_type: Literal["movies", "shows", "seasons", "episodes"] | None = None
    item_id: str | None = None
    start_at: str | None = None
    end_at: str | None = None
    page: int | None = Field(default=None, ge=1, description="Page number (1-based)")

    @field_validator("history_type", "item_id", "start_at", "end_at", mode="before")
    @classmethod
    def _empty_to_none(cls, v: object) -> object:
        """Convert empty strings to None."""
        if isinstance(v, str):
            stripped = v.strip()
            return None if stripped == "" else stripped
        return v

    @field_validator("start_at", "end_at")
    @classmethod
    def _validate_iso8601(cls, v: str | None) -> str | None:
        """Validate ISO 8601 date format."""
        if v is not None:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @model_validator(mode="after")
    def _validate_item_requires_type(self) -> Self:
        """Ensure item_id requires history_type."""
        if self.item_id and not self.history_type:
            raise ValueError("history_type is required when specifying item_id")
        return self
