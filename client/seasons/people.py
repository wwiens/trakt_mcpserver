"""Season people functionality."""

from models.types import PeopleResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


class SeasonPeopleClient(BaseClient):
    """Client for season people (cast and crew) operations."""

    @handle_api_errors
    async def get_season_people(self, show_id: str, season: int) -> PeopleResponse:
        """Get cast and crew for a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)

        Returns:
            People data with cast and crew lists
        """
        show_id = validate_show_id(show_id)
        endpoint = build_season_endpoint("season_people", show_id, season)
        return await self._make_typed_request(endpoint, response_type=PeopleResponse)
