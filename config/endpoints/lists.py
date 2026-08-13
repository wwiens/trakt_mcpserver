"""Lists endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

LISTS_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    "list_items": "/users/:owner/lists/:id/items/:type",
    "trending_lists": "/lists/trending",
    "popular_lists": "/lists/popular",
}
