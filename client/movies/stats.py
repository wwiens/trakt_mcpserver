"""Movie statistics functionality (favorited, played, watched)."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import FavoritedMovieWrapper, PlayedMovieWrapper, WatchedMovieWrapper
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieStatsClient(BaseClient):
    """Client for movie statistics operations."""

    @handle_api_errors
    async def get_favorited_movies(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[FavoritedMovieWrapper]:
        """Get favorited movies from Trakt.

        Args:
            limit: Maximum number of movies to return
            period: Time period for favorited movies

        Returns:
            List of favorited movies data
        """
        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["movies_favorited"],
            response_type=FavoritedMovieWrapper,
            params={"limit": limit, "period": period},
        )

    @handle_api_errors
    async def get_played_movies(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[PlayedMovieWrapper]:
        """Get played movies from Trakt.

        Args:
            limit: Maximum number of movies to return
            period: Time period for played movies

        Returns:
            List of played movies data
        """
        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["movies_played"],
            response_type=PlayedMovieWrapper,
            params={"limit": limit, "period": period},
        )

    @handle_api_errors
    async def get_watched_movies(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[WatchedMovieWrapper]:
        """Get watched movies from Trakt.

        Args:
            limit: Maximum number of movies to return
            period: Time period for watched movies

        Returns:
            List of watched movies data
        """
        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["movies_watched"],
            response_type=WatchedMovieWrapper,
            params={"limit": limit, "period": period},
        )
