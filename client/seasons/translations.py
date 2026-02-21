"""Season translations functionality."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS
from models.types import TranslationResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


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
        """
        show_id = show_id.strip()
        if not show_id:
            raise ValueError("show_id cannot be empty")

        encoded_id = quote(show_id, safe="")
        endpoint = (
            TRAKT_ENDPOINTS["season_translations"]
            .replace(":id", encoded_id)
            .replace(":season", str(season))
            .replace(":language", language)
        )
        return await self._make_typed_list_request(
            endpoint, response_type=TranslationResponse
        )
