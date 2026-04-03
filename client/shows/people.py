"""Show people functionality."""

from urllib.parse import quote

from client.validation import validate_media_id
from config.endpoints import TRAKT_ENDPOINTS
from models.types import PeopleResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowPeopleClient(BaseClient):
    """Client for show people (cast and crew) operations."""

    @handle_api_errors
    async def get_show_people(
        self,
        show_id: str,
        include_guest_stars: bool = False,
    ) -> PeopleResponse:
        """Get cast and crew for a specific show.

        Args:
            show_id: Trakt ID, Trakt slug, or IMDB ID
            include_guest_stars: Include guest stars in response

        Returns:
            People data with cast, crew, and optionally guest stars
        """
        show_id = validate_media_id(show_id, "show_id")

        endpoint = TRAKT_ENDPOINTS["show_people"].replace(
            ":id", quote(show_id, safe="")
        )
        params: dict[str, str] | None = None
        if include_guest_stars:
            params = {"extended": "guest_stars"}

        return await self._make_typed_request(
            endpoint, response_type=PeopleResponse, params=params
        )
