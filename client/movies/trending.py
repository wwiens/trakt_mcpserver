"""Trending movies functionality."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import TrendingWrapper
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class TrendingMoviesClient(BaseClient):
    """Client for trending movies operations."""

    @handle_api_errors
    async def get_trending_movies(
        self, limit: int = DEFAULT_LIMIT
    ) -> list[TrendingWrapper]:
        """Get trending movies from Trakt.

        Args:
            limit: Maximum number of movies to return

        Returns:
            List of trending movies data
        """
        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["movies_trending"],
            response_type=TrendingWrapper,
            params={"limit": limit},
        )
