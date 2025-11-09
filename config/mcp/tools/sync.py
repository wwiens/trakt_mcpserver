"""Sync-specific MCP tool name definitions."""

from collections.abc import Mapping
from typing import Final

# Sync MCP Tool Names (for user personal data requiring OAuth)
SYNC_TOOLS: Final[Mapping[str, str]] = {
    "fetch_user_ratings": "fetch_user_ratings",
    "add_user_ratings": "add_user_ratings",
    "remove_user_ratings": "remove_user_ratings",
    "fetch_user_watchlist": "fetch_user_watchlist",
    "add_user_watchlist": "add_user_watchlist",
    "remove_user_watchlist": "remove_user_watchlist",
}

__all__ = ["SYNC_TOOLS"]
