"""Season info functionality."""

from models.types import SeasonResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


class SeasonInfoClient(BaseClient):
    """Client for season info operations."""

    @handle_api_errors
    async def get_season(self, show_id: str, season: int) -> SeasonResponse:
        """Get details for a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)

        Returns:
            Season details data
        """
        show_id = validate_show_id(show_id)
        endpoint = build_season_endpoint("season_info", show_id, season)
        params = {"extended": "full"}
        return await self._make_typed_request(
            endpoint, response_type=SeasonResponse, params=params
        )
