"""Sync API constants for the Trakt MCP server."""

# Rating constants
RATING_MIN = 1
RATING_MAX = 10
RATING_SCALE = list(range(RATING_MIN, RATING_MAX + 1))

# Valid rating types
RATING_TYPES = ["movies", "shows", "seasons", "episodes"]

# Default parameters for sync operations
DEFAULT_SYNC_LIMIT = None  # No default limit for sync operations
