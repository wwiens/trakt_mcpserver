"""Movie people functionality."""

from urllib.parse import quote

from client.validation import validate_media_id
from config.endpoints import TRAKT_ENDPOINTS
from models.types import PeopleResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MoviePeopleClient(BaseClient):
    """Client for movie people (cast and crew) operations."""

    @handle_api_errors
    async def get_movie_people(self, movie_id: str) -> PeopleResponse:
        """Get cast and crew for a specific movie.

        Args:
            movie_id: Trakt ID, Trakt slug, or IMDB ID

        Returns:
            People data with cast and crew lists
        """
        movie_id = validate_media_id(movie_id, "movie_id")

        endpoint = TRAKT_ENDPOINTS["movie_people"].replace(
            ":id", quote(movie_id, safe="")
        )
        return await self._make_typed_request(endpoint, response_type=PeopleResponse)
