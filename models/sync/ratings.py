"""Sync ratings models for the Trakt MCP server."""

from typing import Literal

from pydantic import BaseModel, Field

from models.movies.movie import TraktMovie
from models.shows.episode import TraktEpisode
from models.shows.show import TraktShow


class TraktSeason(BaseModel):
    """Represents a Trakt season for ratings."""

    number: int
    ids: dict[str, str | int | None] | None = None


class TraktSyncRating(BaseModel):
    """Individual rating item from sync API."""

    rated_at: str = Field(description="ISO timestamp when rated")
    rating: int = Field(ge=1, le=10, description="Rating from 1 to 10")
    type: Literal["movie", "show", "season", "episode"]
    movie: TraktMovie | None = None
    show: TraktShow | None = None
    season: TraktSeason | None = None
    episode: TraktEpisode | None = None


class TraktSyncRatingItem(BaseModel):
    """Rating item for POST/DELETE requests."""

    rating: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Rating from 1 to 10 (required for POST, optional for DELETE)",
    )
    rated_at: str | None = Field(default=None, description="ISO timestamp when rated")
    title: str | None = None
    year: int | None = None
    ids: dict[str, str | int | None] | None = None
    # For episodes within shows
    seasons: list["TraktSyncSeasonRating"] | None = None


class TraktSyncSeasonRating(BaseModel):
    """Season rating item for nested ratings within shows."""

    rating: int | None = Field(default=None, ge=1, le=10, description="Season rating")
    number: int
    episodes: list["TraktSyncEpisodeRating"] | None = None


class TraktSyncEpisodeRating(BaseModel):
    """Episode rating item for nested ratings within seasons."""

    rating: int = Field(ge=1, le=10, description="Episode rating")
    number: int


class TraktSyncRatingsRequest(BaseModel):
    """Request structure for POST/DELETE sync ratings operations."""

    movies: list[TraktSyncRatingItem] | None = None
    shows: list[TraktSyncRatingItem] | None = None
    seasons: list[TraktSyncRatingItem] | None = None
    episodes: list[TraktSyncRatingItem] | None = None


class SyncRatingsSummaryCount(BaseModel):
    """Summary counts for add/remove operations."""

    movies: int = 0
    shows: int = 0
    seasons: int = 0
    episodes: int = 0


class SyncRatingsNotFound(BaseModel):
    """Items not found during add/remove operations."""

    movies: list[TraktSyncRatingItem] = Field(default_factory=lambda: [])
    shows: list[TraktSyncRatingItem] = Field(default_factory=lambda: [])
    seasons: list[TraktSyncRatingItem] = Field(default_factory=lambda: [])
    episodes: list[TraktSyncRatingItem] = Field(default_factory=lambda: [])


class SyncRatingsSummary(BaseModel):
    """Add/remove operation summary with counts and errors."""

    added: SyncRatingsSummaryCount | None = None
    removed: SyncRatingsSummaryCount | None = None
    not_found: SyncRatingsNotFound


class TraktSyncRatingsResponse(BaseModel):
    """Response structure from sync ratings API."""

    ratings: list[TraktSyncRating] = Field(default_factory=lambda: [])


# Update forward references for nested models
TraktSyncRatingItem.model_rebuild()
TraktSyncSeasonRating.model_rebuild()
