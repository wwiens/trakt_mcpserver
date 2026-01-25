"""Show progress client for Trakt API."""

from typing import Any, Literal
from urllib.parse import quote

from config.endpoints.progress import PROGRESS_ENDPOINTS
from models.progress.show_progress import ShowProgressResponse
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


class ShowProgressClient(AuthClient):
    """Client for show progress operations."""

    @handle_api_errors
    async def get_show_progress(
        self,
        show_id: str,
        *,
        hidden: bool = False,
        specials: bool = False,
        count_specials: bool = True,
        last_activity: Literal["aired", "watched"] = "aired",
    ) -> ShowProgressResponse:
        """Get watched progress for a show.

        Args:
            show_id: Trakt ID, slug, or IMDB ID of the show
            hidden: Include hidden seasons in progress calculation
            specials: Include specials as season 0 in progress
            count_specials: Count specials in overall stats when specials included
            last_activity: Calculate last/next episode based on 'aired' or 'watched'

        Returns:
            Show progress response with aired/completed counts and episode details

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to access show progress")

        # Build the endpoint URL with URL-encoded show_id
        endpoint = PROGRESS_ENDPOINTS["show_progress_watched"].replace(
            ":id", quote(show_id, safe="")
        )

        # Build query parameters
        params: dict[str, Any] = {
            "hidden": str(hidden).lower(),
            "specials": str(specials).lower(),
            "count_specials": str(count_specials).lower(),
            "last_activity": last_activity,
        }

        return await self._make_typed_request(
            endpoint, response_type=ShowProgressResponse, params=params
        )
