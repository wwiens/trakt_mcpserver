"""Movie statistics functionality (favorited, played, watched)."""

from typing import Any

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieStatsClient(BaseClient):
    """Client for movie statistics operations."""

    @handle_api_errors
    async def get_favorited_movies(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[dict[str, Any]]:
        """Get favorited movies from Trakt.

        Args:
            limit: Maximum number of movies to return
            period: Time period for favorited movies

        Returns:
            List of favorited movies data
        """
        return await self._make_list_request(
            TRAKT_ENDPOINTS["movies_favorited"],
            params={"limit": limit, "period": period},
        )

    @handle_api_errors
    async def get_played_movies(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[dict[str, Any]]:
        """Get played movies from Trakt.

        Args:
            limit: Maximum number of movies to return
            period: Time period for played movies

        Returns:
            List of played movies data
        """
        return await self._make_list_request(
            TRAKT_ENDPOINTS["movies_played"], params={"limit": limit, "period": period}
        )

    @handle_api_errors
    async def get_watched_movies(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[dict[str, Any]]:
        """Get watched movies from Trakt.

        Args:
            limit: Maximum number of movies to return
            period: Time period for watched movies

        Returns:
            List of watched movies data
        """
        return await self._make_list_request(
            TRAKT_ENDPOINTS["movies_watched"], params={"limit": limit, "period": period}
        )
