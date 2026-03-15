"""Episode ratings functionality."""

from models.types import TraktRating
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import (
    build_episode_endpoint,
    validate_episode,
    validate_season,
    validate_show_id,
)


class EpisodeRatingsClient(BaseClient):
    """Client for episode ratings operations."""

    @handle_api_errors
    async def get_episode_ratings(
        self, show_id: str, season: int, episode: int
    ) -> TraktRating:
        """Get ratings for a specific episode.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)
            episode: Episode number

        Returns:
            Episode ratings data with distribution
        """
        show_id = validate_show_id(show_id)
        season = validate_season(season)
        episode = validate_episode(episode)
        endpoint = build_episode_endpoint("episode_ratings", show_id, season, episode)
        return await self._make_typed_request(endpoint, response_type=TraktRating)
