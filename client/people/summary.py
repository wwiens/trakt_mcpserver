"""Person summary functionality."""

from models.types import PersonResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_person_endpoint, validate_person_id


class PersonSummaryClient(BaseClient):
    """Client for person summary operations."""

    @handle_api_errors
    async def get_person(self, person_id: str) -> PersonResponse:
        """Get basic details for a specific person.

        Args:
            person_id: Trakt ID, Trakt slug, or IMDB ID

        Returns:
            Person data with name and IDs
        """
        person_id = validate_person_id(person_id)
        endpoint = build_person_endpoint("person_summary", person_id)
        return await self._make_typed_request(endpoint, response_type=PersonResponse)

    @handle_api_errors
    async def get_person_extended(self, person_id: str) -> PersonResponse:
        """Get extended details for a specific person.

        Args:
            person_id: Trakt ID, Trakt slug, or IMDB ID

        Returns:
            Extended person data including biography, birthday, social IDs
        """
        person_id = validate_person_id(person_id)
        endpoint = build_person_endpoint("person_summary", person_id)
        params = {"extended": "full"}
        return await self._make_typed_request(
            endpoint, response_type=PersonResponse, params=params
        )
