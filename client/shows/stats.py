"""Show statistics functionality (favorited, played, watched)."""

from typing import Any

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowStatsClient(BaseClient):
    """Client for show statistics operations."""

    @handle_api_errors
    async def get_favorited_shows(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[dict[str, Any]]:
        """Get favorited shows from Trakt.

        Args:
            limit: Maximum number of shows to return
            period: Time period for favorited shows

        Returns:
            List of favorited shows data
        """
        return await self._make_list_request(
            TRAKT_ENDPOINTS["shows_favorited"],
            params={"limit": limit, "period": period},
        )

    @handle_api_errors
    async def get_played_shows(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[dict[str, Any]]:
        """Get played shows from Trakt.

        Args:
            limit: Maximum number of shows to return
            period: Time period for played shows

        Returns:
            List of played shows data
        """
        return await self._make_list_request(
            TRAKT_ENDPOINTS["shows_played"], params={"limit": limit, "period": period}
        )

    @handle_api_errors
    async def get_watched_shows(
        self, limit: int = DEFAULT_LIMIT, period: str = "weekly"
    ) -> list[dict[str, Any]]:
        """Get watched shows from Trakt.

        Args:
            limit: Maximum number of shows to return
            period: Time period for watched shows

        Returns:
            List of watched shows data
        """
        return await self._make_list_request(
            TRAKT_ENDPOINTS["shows_watched"], params={"limit": limit, "period": period}
        )
