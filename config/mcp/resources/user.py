"""User-specific MCP resource URI definitions."""

from typing import Final

# User MCP Resource URIs
USER_RESOURCES: Final[dict[str, str]] = {
    "user_auth_status": "trakt://user/auth/status",
    "user_watched_shows": "trakt://user/watched/shows",
    "user_watched_movies": "trakt://user/watched/movies",
}
