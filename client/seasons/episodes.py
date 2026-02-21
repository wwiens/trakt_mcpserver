"""Season episodes functionality."""

from models.types import EpisodeResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


class SeasonEpisodesClient(BaseClient):
    """Client for season episodes operations."""

    @handle_api_errors
    async def get_season_episodes(
        self, show_id: str, season: int
    ) -> list[EpisodeResponse]:
        """Get all episodes for a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)

        Returns:
            List of episode data
        """
        show_id = validate_show_id(show_id)
        endpoint = build_season_endpoint("season_episodes", show_id, season)
        params = {"extended": "full"}
        return await self._make_typed_list_request(
            endpoint, response_type=EpisodeResponse, params=params
        )
