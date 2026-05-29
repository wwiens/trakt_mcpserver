"""List API constants for the Trakt MCP server."""

from typing import Final

VALID_LIST_TYPES: Final[frozenset[str]] = frozenset(
    {"all", "personal", "official", "watchlists"}
)

VALID_LIST_SORTS: Final[frozenset[str]] = frozenset(
    {"popular", "likes", "comments", "items", "added", "updated"}
)
