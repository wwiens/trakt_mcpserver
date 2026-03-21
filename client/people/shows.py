"""Person show credits functionality."""

from models.types import PersonShowCreditsResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_person_endpoint, validate_person_id


class PersonShowsClient(BaseClient):
    """Client for person show credits operations."""

    @handle_api_errors
    async def get_person_shows(self, person_id: str) -> PersonShowCreditsResponse:
        """Get all show credits for a specific person.

        Args:
            person_id: Trakt ID, Trakt slug, or IMDB ID

        Returns:
            Show credits with cast and crew roles
        """
        person_id = validate_person_id(person_id)
        endpoint = build_person_endpoint("person_shows", person_id)
        return await self._make_typed_request(
            endpoint, response_type=PersonShowCreditsResponse
        )
