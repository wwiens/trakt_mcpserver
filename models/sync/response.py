"""Sync response models for the Trakt MCP server."""

from typing import Annotated

from pydantic import BaseModel, Field

from models.sync.base import TraktSyncRating


class TraktSyncRatingsResponse(BaseModel):
    """Response structure from sync ratings API."""

    ratings: Annotated[list[TraktSyncRating], Field(default_factory=list)]
