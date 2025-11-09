"""Show details functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import ShowResponse, TraktRating
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowDetailsClient(BaseClient):
    """Client for show details operations."""

    @handle_api_errors
    async def get_show(self, show_id: str) -> ShowResponse:
        """Get details for a specific show.

        Args:
            show_id: The Trakt show ID

        Returns:
            Show details data
        """
        endpoint = f"/shows/{quote(show_id, safe='')}"
        return await self._make_typed_request(endpoint, response_type=ShowResponse)

    @handle_api_errors
    async def get_show_extended(self, show_id: str) -> ShowResponse:
        """Get extended details for a specific show.

        Args:
            show_id: The Trakt show ID

        Returns:
            Extended show details data including airs object, status, enhanced overview
        """
        endpoint = f"/shows/{quote(show_id, safe='')}"
        params = {"extended": "full"}
        return await self._make_typed_request(
            endpoint, response_type=ShowResponse, params=params
        )

    @handle_api_errors
    async def get_show_ratings(self, show_id: str) -> TraktRating:
        """Get ratings for a specific show.

        Args:
            show_id: The Trakt show ID

        Returns:
            Show ratings data
        """
        endpoint = TRAKT_ENDPOINTS["show_ratings"].replace(
            ":id", quote(show_id, safe="")
        )
        return await self._make_typed_request(endpoint, response_type=TraktRating)
