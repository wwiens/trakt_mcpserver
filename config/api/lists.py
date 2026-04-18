"""List API constants for the Trakt MCP server."""

from typing import Final

VALID_LIST_TYPES: Final[frozenset[str]] = frozenset(
    {"all", "personal", "official", "watchlists"}
)

VALID_LIST_SORTS: Final[frozenset[str]] = frozenset(
    {"popular", "likes", "comments", "items", "added", "updated"}
)

INVALID_LIST_TYPE_MSG: Final[str] = (
    f"list_type must be one of: {', '.join(sorted(VALID_LIST_TYPES))}"
)
INVALID_LIST_SORT_MSG: Final[str] = (
    f"sort must be one of: {', '.join(sorted(VALID_LIST_SORTS))}"
)
