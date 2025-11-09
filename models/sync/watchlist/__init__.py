"""Sync watchlist models for the Trakt MCP server."""

# Re-export all models from split files
from .base import (
    TraktSeason,
    TraktSyncEpisodeWatchlist,
    TraktSyncSeasonWatchlist,
    TraktSyncWatchlistItem,
    TraktWatchlistItem,
)
from .request import TraktSyncWatchlistRequest
from .response import (
    SyncWatchlistNotFound,
    SyncWatchlistSummary,
    SyncWatchlistSummaryCount,
)

__all__ = [
    "SyncWatchlistNotFound",
    "SyncWatchlistSummary",
    "SyncWatchlistSummaryCount",
    "TraktSeason",
    "TraktSyncEpisodeWatchlist",
    "TraktSyncSeasonWatchlist",
    "TraktSyncWatchlistItem",
    "TraktSyncWatchlistRequest",
    "TraktWatchlistItem",
]
