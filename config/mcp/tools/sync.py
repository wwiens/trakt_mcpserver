"""Sync-specific MCP tool name definitions (user personal data requiring OAuth)."""

from typing import Final

SYNC_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_user_ratings",
        "add_user_ratings",
        "remove_user_ratings",
        "fetch_user_watchlist",
        "add_user_watchlist",
        "remove_user_watchlist",
        "fetch_history",
        "add_to_history",
        "remove_from_history",
    }
)

__all__ = ["SYNC_TOOLS"]
