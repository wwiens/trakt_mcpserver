"""Show progress client for Trakt API."""

from typing import Literal
from urllib.parse import quote

from pydantic import BaseModel, Field, field_validator

from config.endpoints.progress import PROGRESS_ENDPOINTS
from models.progress.show_progress import ShowProgressResponse
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


class ShowProgressParams(BaseModel):
    """Parameters for show progress API requests."""

    show_id: str = Field(..., min_length=1)
    hidden: bool = False
    specials: bool = False
    count_specials: bool = True
    last_activity: Literal["aired", "watched"] = "aired"

    @field_validator("show_id", mode="before")
    @classmethod
    def _strip_show_id(cls, v: object) -> object:
        """Strip whitespace from show_id if string."""
        return v.strip() if isinstance(v, str) else v


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

        validated = ShowProgressParams(
            show_id=show_id,
            hidden=hidden,
            specials=specials,
            count_specials=count_specials,
            last_activity=last_activity,
        )

        endpoint = PROGRESS_ENDPOINTS["show_progress_watched"].replace(
            ":id", quote(validated.show_id, safe="")
        )

        params: dict[str, str] = {
            "hidden": str(validated.hidden).lower(),
            "specials": str(validated.specials).lower(),
            "count_specials": str(validated.count_specials).lower(),
            "last_activity": validated.last_activity,
        }

        return await self._make_typed_request(
            endpoint, response_type=ShowProgressResponse, params=params
        )
