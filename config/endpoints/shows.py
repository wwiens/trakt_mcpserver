"""Show endpoints."""

from typing import Final

SHOWS_ENDPOINTS: Final[dict[str, str]] = {
    # Show endpoints
    "shows_trending": "/shows/trending",
    "shows_popular": "/shows/popular",
    "shows_favorited": "/shows/favorited",
    "shows_played": "/shows/played",
    "shows_watched": "/shows/watched",
    # Rating endpoints
    "show_ratings": "/shows/:id/ratings",
    # Video endpoints
    "show_videos": "/shows/:id/videos",
    # Related endpoints
    "shows_related": "/shows/:id/related",
}
