"""Season stats functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import SeasonStatsResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SeasonStatsClient(BaseClient):
    """Client for season stats operations."""

    @handle_api_errors
    async def get_season_stats(self, show_id: str, season: int) -> SeasonStatsResponse:
        """Get statistics for a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)

        Returns:
            Season statistics data
        """
        show_id = show_id.strip()
        if not show_id:
            raise ValueError("show_id cannot be empty")

        encoded_id = quote(show_id, safe="")
        endpoint = (
            TRAKT_ENDPOINTS["season_stats"]
            .replace(":id", encoded_id)
            .replace(":season", str(season))
        )
        return await self._make_typed_request(
            endpoint, response_type=SeasonStatsResponse
        )
