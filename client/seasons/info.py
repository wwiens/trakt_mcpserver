"""Season info functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import SeasonResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


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
        show_id = show_id.strip()
        if not show_id:
            raise ValueError("show_id cannot be empty")

        encoded_id = quote(show_id, safe="")
        endpoint = (
            TRAKT_ENDPOINTS["season_info"]
            .replace(":id", encoded_id)
            .replace(":season", str(season))
        )
        params = {"extended": "full"}
        return await self._make_typed_request(
            endpoint, response_type=SeasonResponse, params=params
        )
