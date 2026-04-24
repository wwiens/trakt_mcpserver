"""Show endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

SHOWS_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    # Show endpoints
    "shows_trending": "/shows/trending",
    "shows_popular": "/shows/popular",
    "shows_favorited": "/shows/favorited/:period",
    "shows_played": "/shows/played/:period",
    "shows_watched": "/shows/watched/:period",
    "shows_anticipated": "/shows/anticipated",
    # Rating endpoints
    "show_ratings": "/shows/:id/ratings",
    # Video endpoints
    "show_videos": "/shows/:id/videos",
    # Related endpoints
    "shows_related": "/shows/:id/related",
    # Season endpoints
    "show_seasons": "/shows/:id/seasons",
    # People endpoints
    "show_people": "/shows/:id/people",
}
