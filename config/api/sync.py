"""Sync API constants for the Trakt MCP server."""

from typing import Final

# Rating constants
RATING_MIN: Final[int] = 1
RATING_MAX: Final[int] = 10
RATING_SCALE: Final[tuple[int, ...]] = tuple(range(RATING_MIN, RATING_MAX + 1))

# Valid rating types
RATING_TYPES: Final[tuple[str, ...]] = ("movies", "shows", "seasons", "episodes")
