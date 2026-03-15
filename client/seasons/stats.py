"""Season stats functionality."""

from models.types import SeasonStatsResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


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
        show_id = validate_show_id(show_id)
        endpoint = build_season_endpoint("season_stats", show_id, season)
        return await self._make_typed_request(
            endpoint, response_type=SeasonStatsResponse
        )
