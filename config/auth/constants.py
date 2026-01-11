"""Authentication constants for the Trakt MCP server."""

from typing import Final

# Authentication constants
AUTH_POLL_INTERVAL: Final[int] = 5  # seconds
AUTH_EXPIRATION: Final[int] = 600  # seconds (10 minutes)
AUTH_VERIFICATION_URL: Final[str] = "https://trakt.tv/activate"
