"""Episode videos functionality."""

from models.types import VideoResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import (
    build_episode_endpoint,
    validate_episode,
    validate_season,
    validate_show_id,
)


class EpisodeVideosClient(BaseClient):
    """Client for episode videos operations."""

    @handle_api_errors
    async def get_episode_videos(
        self, show_id: str, season: int, episode: int
    ) -> list[VideoResponse]:
        """Get videos for a specific episode.

        Args:
            show_id: Trakt ID, Trakt slug, IMDB ID (tt prefix), TMDB ID, or TVDB ID
            season: Season number (0 for specials)
            episode: Episode number

        Returns:
            List of video response data
        """
        show_id = validate_show_id(show_id)
        season = validate_season(season)
        episode = validate_episode(episode)
        endpoint = build_episode_endpoint("episode_videos", show_id, season, episode)
        return await self._make_typed_list_request(
            endpoint, response_type=VideoResponse
        )
