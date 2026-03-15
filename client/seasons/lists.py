"""Season lists functionality."""

from typing import Literal

from models.types import ListItemResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


class SeasonListsClient(BaseClient):
    """Client for season lists operations."""

    @handle_api_errors
    async def get_season_lists(
        self,
        show_id: str,
        season: int,
        list_type: Literal["all", "personal", "official", "watchlists"] = "all",
        sort: Literal[
            "popular", "likes", "comments", "items", "added", "updated"
        ] = "popular",
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
        show_id = validate_show_id(show_id)
        endpoint = build_season_endpoint(
            "season_lists", show_id, season, type=list_type, sort=sort
        )
        return await self._make_typed_list_request(
            endpoint, response_type=ListItemResponse
        )
