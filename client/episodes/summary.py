"""Episode summary functionality."""

from models.types import EpisodeResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_episode_endpoint, validate_show_id


class EpisodeSummaryClient(BaseClient):
    """Client for episode summary operations."""

    @handle_api_errors
    async def get_episode(
        self, show_id: str, season: int, episode: int
    ) -> EpisodeResponse:
        """Get details for a specific episode.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)
            episode: Episode number

        Returns:
            Episode details data
        """
        show_id = validate_show_id(show_id)
        endpoint = build_episode_endpoint("episode_summary", show_id, season, episode)
        params = {"extended": "full"}
        return await self._make_typed_request(
            endpoint, response_type=EpisodeResponse, params=params
        )
