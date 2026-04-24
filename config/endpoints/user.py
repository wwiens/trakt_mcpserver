"""User endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

USER_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    # User endpoints
    "user_watched_shows": "/sync/watched/shows",
    "user_watched_movies": "/sync/watched/movies",
}
