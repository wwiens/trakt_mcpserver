"""Season watching functionality."""

from models.types import UserResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


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
        show_id = validate_show_id(show_id)
        endpoint = build_season_endpoint("season_watching", show_id, season)
        return await self._make_typed_list_request(endpoint, response_type=UserResponse)
