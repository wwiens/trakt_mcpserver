"""Base sync models for the Trakt MCP server."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from models.movies.movie import TraktMovie
from models.shows.episode import TraktEpisode
from models.shows.show import TraktShow


class TraktSeason(BaseModel):
    """Represents a Trakt season for ratings."""

    number: int = Field(ge=0)  # Season 0 is typically specials
    ids: dict[str, str | int | None] | None = None


class TraktSyncEpisodeRating(BaseModel):
    """Episode rating item for nested ratings within seasons."""

    rating: int = Field(ge=1, le=10, description="Episode rating")
    number: int = Field(ge=1)  # Episode numbers start at 1


class TraktSyncSeasonRating(BaseModel):
    """Season rating item for nested ratings within shows."""

    rating: int | None = Field(default=None, ge=1, le=10, description="Season rating")
    number: int = Field(ge=0)  # Season 0 is typically specials
    episodes: list[TraktSyncEpisodeRating] | None = None


class TraktSyncRatingItem(BaseModel):
    """Rating item for POST/DELETE requests."""

    rating: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Rating from 1 to 10 (required for POST, optional for DELETE)",
    )
    rated_at: datetime | None = Field(
        default=None, description="Timestamp when rated (UTC)"
    )
    title: str | None = None
    year: int | None = Field(default=None, gt=1800)  # Reasonable year constraint
    ids: dict[str, str | int | None] | None = None
    # For episodes within shows
    seasons: list[TraktSyncSeasonRating] | None = None


class TraktSyncRating(BaseModel):
    """Individual rating item from sync API."""

    rated_at: datetime = Field(description="Timestamp when rated (UTC)")
    rating: int = Field(ge=1, le=10, description="Rating from 1 to 10")
    type: Literal["movie", "show", "season", "episode"]
    movie: TraktMovie | None = None
    show: TraktShow | None = None
    season: TraktSeason | None = None
    episode: TraktEpisode | None = None
