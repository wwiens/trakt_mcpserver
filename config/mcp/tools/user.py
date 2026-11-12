"""User-specific MCP tool name definitions."""

from typing import Final

USER_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_user_watched_shows",
        "fetch_user_watched_movies",
        "fetch_user_lists",
        "create_user_list",
        "update_user_list",
        "delete_user_list",
        "add_user_list_items",
        "remove_user_list_items",
    }
)
