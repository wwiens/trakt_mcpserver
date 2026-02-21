"""Season episodes functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import EpisodeResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


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
        show_id = show_id.strip()
        if not show_id:
            raise ValueError("show_id cannot be empty")

        encoded_id = quote(show_id, safe="")
        endpoint = (
            TRAKT_ENDPOINTS["season_episodes"]
            .replace(":id", encoded_id)
            .replace(":season", str(season))
        )
        params = {"extended": "full"}
        return await self._make_typed_list_request(
            endpoint, response_type=EpisodeResponse, params=params
        )
