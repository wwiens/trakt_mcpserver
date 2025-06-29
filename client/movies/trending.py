"""Trending movies functionality."""

from typing import Any

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class TrendingMoviesClient(BaseClient):
    """Client for trending movies operations."""

    @handle_api_errors
    async def get_trending_movies(
        self, limit: int = DEFAULT_LIMIT
    ) -> list[dict[str, Any]]:
        """Get trending movies from Trakt.

        Args:
            limit: Maximum number of movies to return

        Returns:
            List of trending movies data
        """
        return await self._make_list_request(
            TRAKT_ENDPOINTS["movies_trending"], params={"limit": limit}
        )
