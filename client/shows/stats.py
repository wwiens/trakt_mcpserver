"""Show statistics functionality (favorited, played, watched)."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import FavoritedShowWrapper, PlayedShowWrapper, WatchedShowWrapper
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowStatsClient(BaseClient):
    """Client for show statistics operations."""

    @handle_api_errors
    async def get_favorited_shows(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[FavoritedShowWrapper]:
        """Get favorited shows from Trakt.

        Args:
            limit: Maximum number of shows to return
            period: Time period for favorited shows

        Returns:
            List of favorited shows data
        """
        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["shows_favorited"],
            response_type=FavoritedShowWrapper,
            params={"limit": limit, "period": period},
        )

    @handle_api_errors
    async def get_played_shows(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[PlayedShowWrapper]:
        """Get played shows from Trakt.

        Args:
            limit: Maximum number of shows to return
            period: Time period for played shows

        Returns:
            List of played shows data
        """
        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["shows_played"],
            response_type=PlayedShowWrapper,
            params={"limit": limit, "period": period},
        )

    @handle_api_errors
    async def get_watched_shows(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[WatchedShowWrapper]:
        """Get watched shows from Trakt.

        Args:
            limit: Maximum number of shows to return
            period: Time period for watched shows

        Returns:
            List of watched shows data
        """
        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["shows_watched"],
            response_type=WatchedShowWrapper,
            params={"limit": limit, "period": period},
        )
