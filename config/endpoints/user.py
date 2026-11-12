"""User endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

USER_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    # User endpoints
    "user_watched_shows": "/sync/watched/shows",
    "user_watched_movies": "/sync/watched/movies",
    "user_lists": "/users/:id/lists",
    "user_list": "/users/:id/lists/:list_id",
    "user_list_items": "/users/:id/lists/:list_id/items",
    "user_list_items_remove": "/users/:id/lists/:list_id/items/remove",
}
