"""Season watching functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import UserResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SeasonWatchingClient(BaseClient):
    """Client for season watching operations."""

    @handle_api_errors
    async def get_season_watching(
        self, show_id: str, season: int
    ) -> list[UserResponse]:
        """Get users currently watching a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)

        Returns:
            List of users currently watching
        """
        show_id = show_id.strip()
        if not show_id:
            raise ValueError("show_id cannot be empty")

        encoded_id = quote(show_id, safe="")
        endpoint = (
            TRAKT_ENDPOINTS["season_watching"]
            .replace(":id", encoded_id)
            .replace(":season", str(season))
        )
        return await self._make_typed_list_request(endpoint, response_type=UserResponse)
