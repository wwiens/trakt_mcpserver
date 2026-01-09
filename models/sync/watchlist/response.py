"""Sync watchlist summary models for the Trakt MCP server."""

from typing import Annotated

from pydantic import BaseModel, Field

from .base import TraktSyncWatchlistItem


class SyncWatchlistSummaryCount(BaseModel):
    """Summary counts for add/remove operations."""

    movies: int = Field(default=0, ge=0)
    shows: int = Field(default=0, ge=0)
    seasons: int = Field(default=0, ge=0)
    episodes: int = Field(default=0, ge=0)


class SyncWatchlistNotFound(BaseModel):
    """Items not found during add/remove operations."""

    movies: Annotated[list[TraktSyncWatchlistItem], Field(default_factory=list)]
    shows: Annotated[list[TraktSyncWatchlistItem], Field(default_factory=list)]
    seasons: Annotated[list[TraktSyncWatchlistItem], Field(default_factory=list)]
    episodes: Annotated[list[TraktSyncWatchlistItem], Field(default_factory=list)]


class SyncWatchlistSummary(BaseModel):
    """Add/remove operation summary with counts and errors."""

    added: SyncWatchlistSummaryCount | None = None
    existing: SyncWatchlistSummaryCount | None = None
    deleted: SyncWatchlistSummaryCount | None = None
    not_found: SyncWatchlistNotFound = Field(
        default_factory=lambda: SyncWatchlistNotFound(
            movies=[], shows=[], seasons=[], episodes=[]
        )
    )
