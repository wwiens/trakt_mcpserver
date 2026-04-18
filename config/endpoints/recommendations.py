"""Trakt API endpoints for recommendations."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

RECOMMENDATIONS_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    "recommendations_movies": "/recommendations/movies",
    "recommendations_shows": "/recommendations/shows",
    "hide_movie_recommendation": "/recommendations/movies/:id",
    "hide_show_recommendation": "/recommendations/shows/:id",
    "unhide_recommendations": "/users/hidden/recommendations/remove",
}
