"""Sync ratings models for the Trakt MCP server."""

# Re-export all models from split files for backward compatibility
from .base import (
    TraktSeason,
    TraktSyncEpisodeRating,
    TraktSyncRating,
    TraktSyncRatingItem,
    TraktSyncSeasonRating,
)
from .request import TraktSyncRatingsRequest
from .response import TraktSyncRatingsResponse
from .summary import SyncRatingsNotFound, SyncRatingsSummary, SyncRatingsSummaryCount

__all__ = [
    "SyncRatingsNotFound",
    "SyncRatingsSummary",
    "SyncRatingsSummaryCount",
    "TraktSeason",
    "TraktSyncEpisodeRating",
    "TraktSyncRating",
    "TraktSyncRatingItem",
    "TraktSyncRatingsRequest",
    "TraktSyncRatingsResponse",
    "TraktSyncSeasonRating",
]
