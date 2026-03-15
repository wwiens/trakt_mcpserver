"""Season ratings functionality."""

from models.types import TraktRating
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


class SeasonRatingsClient(BaseClient):
    """Client for season ratings operations."""

    @handle_api_errors
    async def get_season_ratings(self, show_id: str, season: int) -> TraktRating:
        """Get ratings for a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)

        Returns:
            Season ratings data with distribution
        """
        show_id = validate_show_id(show_id)
        endpoint = build_season_endpoint("season_ratings", show_id, season)
        return await self._make_typed_request(endpoint, response_type=TraktRating)
