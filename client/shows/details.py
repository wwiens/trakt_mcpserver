"""Show details functionality."""

from typing import Any

from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowDetailsClient(BaseClient):
    """Client for show details operations."""

    @handle_api_errors
    async def get_show(self, show_id: str) -> dict[str, Any]:
        """Get details for a specific show.

        Args:
            show_id: The Trakt show ID

        Returns:
            Show details data
        """
        endpoint = f"/shows/{show_id}"
        return await self._make_dict_request(endpoint)

    @handle_api_errors
    async def get_show_ratings(self, show_id: str) -> dict[str, Any]:
        """Get ratings for a specific show.

        Args:
            show_id: The Trakt show ID

        Returns:
            Show ratings data
        """
        endpoint = TRAKT_ENDPOINTS["show_ratings"].replace(":id", show_id)
        return await self._make_dict_request(endpoint)
