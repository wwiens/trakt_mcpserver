"""Show seasons functionality."""

from urllib.parse import quote

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
        endpoint = f"/shows/{quote(show_id, safe='')}/seasons"
        params = {"extended": "full"}
        return await self._make_typed_list_request(
            endpoint, response_type=SeasonResponse, params=params
        )
