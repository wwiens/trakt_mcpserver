"""Episode lists functionality."""

from typing import Literal

from models.types import ListItemResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_episode_endpoint, validate_show_id


class EpisodeListsClient(BaseClient):
    """Client for episode lists operations."""

    @handle_api_errors
    async def get_episode_lists(
        self,
        show_id: str,
        season: int,
        episode: int,
        list_type: Literal["all", "personal", "official", "watchlists"] = "all",
        sort: Literal[
            "popular", "likes", "comments", "items", "added", "updated"
        ] = "popular",
    ) -> list[ListItemResponse]:
        """Get lists that contain a specific episode.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)
            episode: Episode number
            list_type: Filter by type: 'all', 'personal', 'official', 'watchlists'
            sort: Sort order: 'popular', 'likes', 'comments', 'items', 'added', 'updated'

        Returns:
            List of list data
        """
        show_id = validate_show_id(show_id)
        endpoint = build_episode_endpoint(
            "episode_lists", show_id, season, episode, type=list_type, sort=sort
        )
        return await self._make_typed_list_request(
            endpoint, response_type=ListItemResponse
        )
