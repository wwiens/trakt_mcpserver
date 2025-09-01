"""Sync summary models for the Trakt MCP server."""

from typing import Annotated

from pydantic import BaseModel, Field

from models.sync.base import TraktSyncRatingItem


class SyncRatingsSummaryCount(BaseModel):
    """Summary counts for add/remove operations."""

    movies: int = Field(default=0, ge=0)
    shows: int = Field(default=0, ge=0)
    seasons: int = Field(default=0, ge=0)
    episodes: int = Field(default=0, ge=0)


class SyncRatingsNotFound(BaseModel):
    """Items not found during add/remove operations."""

    movies: Annotated[list[TraktSyncRatingItem], Field(default_factory=list)]
    shows: Annotated[list[TraktSyncRatingItem], Field(default_factory=list)]
    seasons: Annotated[list[TraktSyncRatingItem], Field(default_factory=list)]
    episodes: Annotated[list[TraktSyncRatingItem], Field(default_factory=list)]


def _create_sync_ratings_not_found() -> SyncRatingsNotFound:
    """Factory function to create SyncRatingsNotFound instance."""
    return SyncRatingsNotFound(movies=[], shows=[], seasons=[], episodes=[])


class SyncRatingsSummary(BaseModel):
    """Add/remove operation summary with counts and errors."""

    added: SyncRatingsSummaryCount | None = None
    removed: SyncRatingsSummaryCount | None = None
    not_found: SyncRatingsNotFound = Field(
        default_factory=_create_sync_ratings_not_found
    )
