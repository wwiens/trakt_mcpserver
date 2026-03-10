"""Season translations functionality."""

from models.types import TranslationResponse
from models.types.language import validate_language
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_season_endpoint, validate_show_id


class SeasonTranslationsClient(BaseClient):
    """Client for season translations operations."""

    @handle_api_errors
    async def get_season_translations(
        self, show_id: str, season: int, language: str = "all"
    ) -> list[TranslationResponse]:
        """Get translations for a specific season.

        Args:
            show_id: Trakt ID, slug, or IMDB ID
            season: Season number (0 for specials)
            language: 2-character language code or 'all'

        Returns:
            List of translation data

        Raises:
            ValueError: If language is not 'all' or a 2-letter ISO 639-1 code
        """
        show_id = validate_show_id(show_id)
        language = validate_language(language)
        endpoint = build_season_endpoint(
            "season_translations", show_id, season, language=language
        )
        return await self._make_typed_list_request(
            endpoint, response_type=TranslationResponse
        )
