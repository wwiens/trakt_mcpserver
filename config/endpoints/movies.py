"""Movie endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

MOVIES_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    # Movie endpoints
    "movies_trending": "/movies/trending",
    "movies_popular": "/movies/popular",
    "movies_favorited": "/movies/favorited/:period",
    "movies_played": "/movies/played/:period",
    "movies_watched": "/movies/watched/:period",
    "movies_anticipated": "/movies/anticipated",
    # Rating endpoints
    "movie_ratings": "/movies/:id/ratings",
    # Video endpoints
    "movie_videos": "/movies/:id/videos",
    # Related endpoints
    "movies_related": "/movies/:id/related",
    # Box office endpoints
    "movies_boxoffice": "/movies/boxoffice",
    # People endpoints
    "movie_people": "/movies/:id/people",
}
