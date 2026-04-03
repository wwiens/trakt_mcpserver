"""People endpoints."""

from typing import Final

PEOPLE_ENDPOINTS: Final[dict[str, str]] = {
    "person_summary": "/people/:id",
    "person_movies": "/people/:id/movies",
    "person_shows": "/people/:id/shows",
    "person_lists": "/people/:id/lists/:type/:sort",
}
