"""Sync API constants for the Trakt MCP server."""

from typing import Final

# Rating constants
RATING_MIN: Final[int] = 1
RATING_MAX: Final[int] = 10
RATING_SCALE: Final[tuple[int, ...]] = tuple(range(RATING_MIN, RATING_MAX + 1))

# Valid rating types
RATING_TYPES: Final[tuple[str, ...]] = ("movies", "shows", "seasons", "episodes")
# If needed by models, the singular item kinds:
# RATING_ITEM_TYPES: Final[tuple[str, ...]] = ("movie", "show", "season", "episode")

# Default parameters for sync operations
DEFAULT_SYNC_LIMIT: Final[int | None] = None  # No default limit for sync operations
