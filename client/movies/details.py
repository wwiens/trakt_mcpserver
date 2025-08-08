"""Movie details functionality."""

from config.endpoints import TRAKT_ENDPOINTS
from models.types import MovieResponse, TraktRating
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieDetailsClient(BaseClient):
    """Client for movie details operations."""

    @handle_api_errors
    async def get_movie(self, movie_id: str) -> MovieResponse:
        """Get details for a specific movie.

        Args:
            movie_id: The Trakt movie ID

        Returns:
            Movie details data
        """
        endpoint = f"/movies/{movie_id}"
        return await self._make_typed_request(endpoint, response_type=MovieResponse)

    @handle_api_errors
    async def get_movie_extended(self, movie_id: str) -> MovieResponse:
        """Get extended details for a specific movie.

        Args:
            movie_id: The Trakt movie ID

        Returns:
            Extended movie details data including status, enhanced overview, and metadata
        """
        endpoint = f"/movies/{movie_id}"
        params = {"extended": "full"}
        return await self._make_typed_request(
            endpoint, response_type=MovieResponse, params=params
        )

    @handle_api_errors
    async def get_movie_ratings(self, movie_id: str) -> TraktRating:
        """Get ratings for a specific movie.

        Args:
            movie_id: The Trakt movie ID

        Returns:
            Movie ratings data
        """
        endpoint = TRAKT_ENDPOINTS["movie_ratings"].replace(":id", movie_id)
        return await self._make_typed_request(endpoint, response_type=TraktRating)
