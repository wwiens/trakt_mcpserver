"""Trending shows functionality."""

from typing import Any

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class TrendingShowsClient(BaseClient):
    """Client for trending shows operations."""

    @handle_api_errors
    async def get_trending_shows(
        self, limit: int = DEFAULT_LIMIT
    ) -> list[dict[str, Any]]:
        """Get trending shows from Trakt.

        Args:
            limit: Maximum number of shows to return

        Returns:
            List of trending shows data
        """
        return await self._make_list_request(
            TRAKT_ENDPOINTS["shows_trending"], params={"limit": limit}
        )
