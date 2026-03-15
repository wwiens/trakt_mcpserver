"""Episode stats functionality."""

from models.types import StatsResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_episode_endpoint, validate_show_id


class EpisodeStatsClient(BaseClient):
    """Client for episode stats operations."""

    @handle_api_errors
    async def get_episode_stats(
        self, show_id: str, season: int, episode: int
    ) -> StatsResponse:
        """Get statistics for a specific episode.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)
            episode: Episode number

        Returns:
            Episode statistics data
        """
        show_id = validate_show_id(show_id)
        endpoint = build_episode_endpoint("episode_stats", show_id, season, episode)
        return await self._make_typed_request(endpoint, response_type=StatsResponse)
