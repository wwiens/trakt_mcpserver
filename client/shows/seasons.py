"""Show seasons functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import SeasonResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowSeasonsClient(BaseClient):
    """Client for show seasons operations."""

    @handle_api_errors
    async def get_seasons(self, show_id: str) -> list[SeasonResponse]:
        """Get all seasons for a specific show with extended details.

        Returns all seasons including episode counts, ratings, and air dates.

        Args:
            show_id: The Trakt show ID, slug, or IMDB ID

        Returns:
            List of season data with episode counts and metadata
        """
        show_id = show_id.strip()
        if not show_id:
            msg = "show_id cannot be empty"
            raise ValueError(msg)

        encoded_id = quote(show_id, safe="")
        endpoint = TRAKT_ENDPOINTS["show_seasons"].replace(":id", encoded_id)
        params = {"extended": "full"}
        return await self._make_typed_list_request(
            endpoint, response_type=SeasonResponse, params=params
        )
