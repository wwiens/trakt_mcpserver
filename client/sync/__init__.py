"""Sync client for the Trakt MCP server."""

from .client import SyncClient
from .history_client import SyncHistoryClient
from .ratings_client import SyncRatingsClient
from .watchlist_client import SyncWatchlistClient

__all__ = [
    "SyncClient",
    "SyncHistoryClient",
    "SyncRatingsClient",
    "SyncWatchlistClient",
]
