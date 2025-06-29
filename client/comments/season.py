"""Season comments functionality."""

from typing import Any

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SeasonCommentsClient(BaseClient):
    """Client for season comments operations."""

    @handle_api_errors
    async def get_season_comments(
        self,
        show_id: str,
        season: int,
        limit: int = DEFAULT_LIMIT,
        page: int = 1,
        sort: str = "newest",
    ) -> list[dict[str, Any]]:
        """Get comments for a season.

        Args:
            show_id: The Trakt show ID
            season: Season number
            limit: Maximum number of comments to return
            page: Page number for pagination
            sort: Sort order for comments

        Returns:
            List of season comments data
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_season"]
            .replace(":id", show_id)
            .replace(":season", str(season))
            .replace(":sort", sort)
        )
        return await self._make_list_request(
            endpoint, params={"limit": limit, "page": page}
        )
