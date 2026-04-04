"""Episode lists functionality."""

from typing import Final, Literal

from models.types import ListItemResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import (
    build_episode_endpoint,
    validate_episode,
    validate_season,
    validate_show_id,
)

VALID_LIST_TYPES: Final[set[str]] = {"all", "personal", "official", "watchlists"}
VALID_SORT_VALUES: Final[set[str]] = {
    "popular",
    "likes",
    "comments",
    "items",
    "added",
    "updated",
}


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
            show_id: Trakt ID, Trakt slug, IMDB ID (tt prefix), TMDB ID, or TVDB ID
            season: Season number (0 for specials)
            episode: Episode number
            list_type: Filter by type: 'all', 'personal', 'official', 'watchlists'
            sort: Sort order: 'popular', 'likes', 'comments', 'items', 'added',
                'updated'

        Returns:
            List of list data

        Raises:
            ValueError: If list_type or sort is not a valid value
        """
        if list_type not in VALID_LIST_TYPES:
            msg = (
                f"list_type must be one of {sorted(VALID_LIST_TYPES)},"
                f" got: '{list_type}'"
            )
            raise ValueError(msg)
        if sort not in VALID_SORT_VALUES:
            msg = f"sort must be one of {sorted(VALID_SORT_VALUES)}, got: '{sort}'"
            raise ValueError(msg)
        show_id = validate_show_id(show_id)
        season = validate_season(season)
        episode = validate_episode(episode)
        endpoint = build_episode_endpoint(
            "episode_lists", show_id, season, episode, type=list_type, sort=sort
        )
        return await self._make_typed_list_request(
            endpoint, response_type=ListItemResponse
        )
