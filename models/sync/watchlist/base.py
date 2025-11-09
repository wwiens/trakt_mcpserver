"""Base watchlist models for the Trakt MCP server."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from models.movies.movie import TraktMovie
from models.shows.episode import TraktEpisode
from models.shows.show import TraktShow


class TraktSeason(BaseModel):
    """Represents a Trakt season for watchlist."""

    number: int = Field(ge=0)  # Season 0 is typically specials
    ids: dict[str, str | int | None] | None = None


class TraktSyncEpisodeWatchlist(BaseModel):
    """Episode watchlist item for nested watchlist within seasons."""

    number: int = Field(ge=1)  # Episode numbers start at 1
    notes: str | None = Field(
        default=None, max_length=500, description="User notes (VIP only)"
    )


class TraktSyncSeasonWatchlist(BaseModel):
    """Season watchlist item for nested watchlist within shows."""

    number: int = Field(ge=0)  # Season 0 is typically specials
    notes: str | None = Field(
        default=None, max_length=500, description="User notes (VIP only)"
    )
    episodes: list[TraktSyncEpisodeWatchlist] | None = None


class TraktSyncWatchlistItem(BaseModel):
    """Watchlist item for POST/DELETE requests."""

    title: str | None = None
    year: int | None = Field(default=None, gt=1800)  # Reasonable year constraint
    ids: dict[str, str | int | None] | None = None
    notes: str | None = Field(
        default=None, max_length=500, description="User notes (VIP only)"
    )
    # For episodes within shows
    seasons: list[TraktSyncSeasonWatchlist] | None = None


class TraktWatchlistItem(BaseModel):
    """Individual watchlist item from sync API."""

    rank: int = Field(ge=1, description="Position in watchlist")
    id: int = Field(ge=1, description="Watchlist item ID")
    listed_at: datetime = Field(description="Timestamp when added (UTC)")
    notes: str | None = Field(
        default=None, max_length=500, description="User notes (VIP only)"
    )
    type: Literal["movie", "show", "season", "episode"]
    movie: TraktMovie | None = None
    show: TraktShow | None = None
    season: TraktSeason | None = None
    episode: TraktEpisode | None = None
