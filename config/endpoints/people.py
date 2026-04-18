"""People endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

PEOPLE_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    "person_summary": "/people/:id",
    "person_movies": "/people/:id/movies",
    "person_shows": "/people/:id/shows",
    "person_lists": "/people/:id/lists/:type/:sort",
}
