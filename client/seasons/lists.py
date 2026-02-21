"""Season lists functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import ListItemResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SeasonListsClient(BaseClient):
    """Client for season lists operations."""

    @handle_api_errors
    async def get_season_lists(
        self,
        show_id: str,
        season: int,
        list_type: str = "all",
        sort: str = "popular",
    ) -> list[ListItemResponse]:
        """Get lists that contain a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)
            list_type: Filter by type: 'all', 'personal', 'official', 'watchlists'
            sort: Sort order: 'popular', 'likes', 'comments', 'items', 'added', 'updated'

        Returns:
            List of list data
        """
        show_id = show_id.strip()
        if not show_id:
            raise ValueError("show_id cannot be empty")

        encoded_id = quote(show_id, safe="")
        endpoint = (
            TRAKT_ENDPOINTS["season_lists"]
            .replace(":id", encoded_id)
            .replace(":season", str(season))
            .replace(":type", list_type)
            .replace(":sort", sort)
        )
        return await self._make_typed_list_request(
            endpoint, response_type=ListItemResponse
        )
