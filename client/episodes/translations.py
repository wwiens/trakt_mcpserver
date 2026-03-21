"""Episode translations functionality."""

from models.types import TranslationResponse
from models.types.language import validate_language
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import (
    build_episode_endpoint,
    validate_episode,
    validate_season,
    validate_show_id,
)


class EpisodeTranslationsClient(BaseClient):
    """Client for episode translations operations."""

    @handle_api_errors
    async def get_episode_translations(
        self, show_id: str, season: int, episode: int, language: str = "all"
    ) -> list[TranslationResponse]:
        """Get translations for a specific episode.

        Args:
            show_id: Trakt ID, Trakt slug, IMDB ID (tt prefix), TMDB ID, or TVDB ID
            season: Season number (0 for specials)
            episode: Episode number
            language: 2-character language code or 'all'

        Returns:
            List of translation data

        Raises:
            ValueError: If language is not 'all' or a 2-letter ISO 639-1 code
        """
        show_id = validate_show_id(show_id)
        season = validate_season(season)
        episode = validate_episode(episode)
        language = validate_language(language)
        endpoint = build_episode_endpoint(
            "episode_translations", show_id, season, episode, language=language
        )
        return await self._make_typed_list_request(
            endpoint, response_type=TranslationResponse
        )
