"""Sync request models for the Trakt MCP server."""

from pydantic import BaseModel, ConfigDict

from .base import TraktSyncRatingItem


class TraktSyncRatingsRequest(BaseModel):
    """Request structure for POST/DELETE sync ratings operations."""

    # Reject unknown fields to avoid silent payload issues
    model_config = ConfigDict(extra="forbid")

    movies: list[TraktSyncRatingItem] | None = None
    shows: list[TraktSyncRatingItem] | None = None
    seasons: list[TraktSyncRatingItem] | None = None
    episodes: list[TraktSyncRatingItem] | None = None
