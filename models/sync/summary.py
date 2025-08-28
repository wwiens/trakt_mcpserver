"""Sync summary models for the Trakt MCP server."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .base import TraktSyncRatingItem  # noqa: TC001  # Required at runtime for Pydantic


class SyncRatingsSummaryCount(BaseModel):
    """Summary counts for add/remove operations."""

    movies: int = Field(default=0, ge=0)
    shows: int = Field(default=0, ge=0)
    seasons: int = Field(default=0, ge=0)
    episodes: int = Field(default=0, ge=0)


class SyncRatingsNotFound(BaseModel):
    """Items not found during add/remove operations."""

    movies: list[TraktSyncRatingItem] = Field(default_factory=list)  # type: ignore[misc]  # Pydantic forward reference
    shows: list[TraktSyncRatingItem] = Field(default_factory=list)  # type: ignore[misc]  # Pydantic forward reference
    seasons: list[TraktSyncRatingItem] = Field(default_factory=list)  # type: ignore[misc]  # Pydantic forward reference
    episodes: list[TraktSyncRatingItem] = Field(default_factory=list)  # type: ignore[misc]  # Pydantic forward reference


class SyncRatingsSummary(BaseModel):
    """Add/remove operation summary with counts and errors."""

    added: SyncRatingsSummaryCount | None = None
    removed: SyncRatingsSummaryCount | None = None
    not_found: SyncRatingsNotFound
