"""Season videos functionality."""

from models.types.api_responses import VideoResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


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
        show_id = validate_show_id(show_id)
        endpoint = build_season_endpoint("season_videos", show_id, season)
        return await self._make_typed_list_request(
            endpoint, response_type=VideoResponse
        )
