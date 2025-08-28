"""Sync response models for the Trakt MCP server."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .base import TraktSyncRating  # noqa: TC001  # Required at runtime for Pydantic


class TraktSyncRatingsResponse(BaseModel):
    """Response structure from sync ratings API."""

    ratings: list[TraktSyncRating] = Field(default_factory=list)  # type: ignore[misc]  # Pydantic forward reference
