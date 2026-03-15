"""Episode watching functionality."""

from models.types import UserResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import (
    build_episode_endpoint,
    validate_episode,
    validate_season,
    validate_show_id,
)


class EpisodeWatchingClient(BaseClient):
    """Client for episode watching operations."""

    @handle_api_errors
    async def get_episode_watching(
        self, show_id: str, season: int, episode: int
    ) -> list[UserResponse]:
        """Get users currently watching a specific episode.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)
            episode: Episode number

        Returns:
            List of users currently watching
        """
        show_id = validate_show_id(show_id)
        season = validate_season(season)
        episode = validate_episode(episode)
        endpoint = build_episode_endpoint("episode_watching", show_id, season, episode)
        return await self._make_typed_list_request(endpoint, response_type=UserResponse)
