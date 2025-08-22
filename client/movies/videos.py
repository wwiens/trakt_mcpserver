"""Movie videos functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types.api_responses import VideoResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieVideosClient(BaseClient):
    """Client for movie videos operations."""

    @handle_api_errors
    async def get_videos(self, movie_id: str) -> list[VideoResponse]:
        """Get videos for a movie.

        Args:
            movie_id: Trakt ID, slug, or IMDB ID

        Returns:
            List of video response data
        """
        movie_id = movie_id.strip()
        if not movie_id:
            raise ValueError("movie_id cannot be empty")

        encoded_id = quote(movie_id, safe="")
        endpoint = TRAKT_ENDPOINTS["movie_videos"].replace(":id", encoded_id)
        return await self._make_typed_list_request(
            endpoint, response_type=VideoResponse
        )
