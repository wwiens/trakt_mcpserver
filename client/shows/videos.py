"""Show videos functionality."""

from config.endpoints import TRAKT_ENDPOINTS
from models.types.api_responses import VideoResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowVideosClient(BaseClient):
    """Client for show videos operations."""

    @handle_api_errors
    async def get_videos(self, show_id: str) -> list[VideoResponse]:
        """Get videos for a show.

        Args:
            show_id: Trakt ID, slug, or IMDB ID

        Returns:
            List of video response data
        """
        endpoint = TRAKT_ENDPOINTS["show_videos"].replace(":id", show_id)
        return await self._make_typed_list_request(
            endpoint, response_type=VideoResponse
        )
