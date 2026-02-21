"""Season videos functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types.api_responses import VideoResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SeasonVideosClient(BaseClient):
    """Client for season videos operations."""

    @handle_api_errors
    async def get_season_videos(self, show_id: str, season: int) -> list[VideoResponse]:
        """Get videos for a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)

        Returns:
            List of video response data
        """
        show_id = show_id.strip()
        if not show_id:
            raise ValueError("show_id cannot be empty")

        encoded_id = quote(show_id, safe="")
        endpoint = (
            TRAKT_ENDPOINTS["season_videos"]
            .replace(":id", encoded_id)
            .replace(":season", str(season))
        )
        return await self._make_typed_list_request(
            endpoint, response_type=VideoResponse
        )
