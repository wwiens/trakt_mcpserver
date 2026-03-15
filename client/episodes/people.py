"""Episode people functionality."""

from models.types import PeopleResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import (
    build_episode_endpoint,
    validate_episode,
    validate_season,
    validate_show_id,
)


class EpisodePeopleClient(BaseClient):
    """Client for episode people (cast and crew) operations."""

    @handle_api_errors
    async def get_episode_people(
        self, show_id: str, season: int, episode: int
    ) -> PeopleResponse:
        """Get cast and crew for a specific episode.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)
            episode: Episode number

        Returns:
            People data with cast and crew lists
        """
        show_id = validate_show_id(show_id)
        season = validate_season(season)
        episode = validate_episode(episode)
        endpoint = build_episode_endpoint("episode_people", show_id, season, episode)
        return await self._make_typed_request(endpoint, response_type=PeopleResponse)
