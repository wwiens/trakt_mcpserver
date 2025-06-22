"""Movie details functionality."""

from typing import Any

from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieDetailsClient(BaseClient):
    """Client for movie details operations."""

    @handle_api_errors
    async def get_movie(self, movie_id: str) -> dict[str, Any]:
        """Get details for a specific movie.

        Args:
            movie_id: The Trakt movie ID

        Returns:
            Movie details data
        """
        endpoint = f"/movies/{movie_id}"
        return await self._make_dict_request(endpoint)

    @handle_api_errors
    async def get_movie_ratings(self, movie_id: str) -> dict[str, Any]:
        """Get ratings for a specific movie.

        Args:
            movie_id: The Trakt movie ID

        Returns:
            Movie ratings data
        """
        endpoint = TRAKT_ENDPOINTS["movie_ratings"].replace(":id", movie_id)
        return await self._make_dict_request(endpoint)
