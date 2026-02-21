"""Season people functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import PeopleResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


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
        show_id = show_id.strip()
        if not show_id:
            raise ValueError("show_id cannot be empty")

        encoded_id = quote(show_id, safe="")
        endpoint = (
            TRAKT_ENDPOINTS["season_people"]
            .replace(":id", encoded_id)
            .replace(":season", str(season))
        )
        return await self._make_typed_request(endpoint, response_type=PeopleResponse)
