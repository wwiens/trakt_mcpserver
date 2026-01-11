"""Movie endpoints."""

from typing import Final

MOVIES_ENDPOINTS: Final[dict[str, str]] = {
    # Movie endpoints
    "movies_trending": "/movies/trending",
    "movies_popular": "/movies/popular",
    "movies_favorited": "/movies/favorited",
    "movies_played": "/movies/played",
    "movies_watched": "/movies/watched",
    # Rating endpoints
    "movie_ratings": "/movies/:id/ratings",
    # Video endpoints
    "movie_videos": "/movies/:id/videos",
}
