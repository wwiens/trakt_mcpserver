"""User-specific MCP tool name definitions."""

from typing import Final

USER_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_user_watched_shows",
        "fetch_user_watched_movies",
    }
)
