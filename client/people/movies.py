"""Person movie credits functionality."""

from models.types import PersonMovieCreditsResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_person_endpoint, validate_person_id


class PersonMoviesClient(BaseClient):
    """Client for person movie credits operations."""

    @handle_api_errors
    async def get_person_movies(self, person_id: str) -> PersonMovieCreditsResponse:
        """Get all movie credits for a specific person.

        Args:
            person_id: Trakt ID, slug, IMDB ID, TMDB ID, or TVDB ID

        Returns:
            Movie credits with cast and crew roles
        """
        person_id = validate_person_id(person_id)
        endpoint = build_person_endpoint("person_movies", person_id)
        return await self._make_typed_request(
            endpoint, response_type=PersonMovieCreditsResponse
        )
