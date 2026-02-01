"""Sync client for the Trakt MCP server."""

from typing import Final

from .client import SyncClient
from .history_client import SyncHistoryClient
from .ratings_client import SyncRatingsClient
from .watchlist_client import SyncWatchlistClient

__all__: Final[list[str]] = [
    "SyncClient",
    "SyncHistoryClient",
    "SyncRatingsClient",
    "SyncWatchlistClient",
]
