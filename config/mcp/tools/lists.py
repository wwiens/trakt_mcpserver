"""Lists-specific MCP tool name definitions."""

from typing import Final

LIST_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_list_items",
        "fetch_trending_lists",
        "fetch_popular_lists",
    }
)
