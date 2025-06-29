"""Show comments functionality."""

from typing import Any

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowCommentsClient(BaseClient):
    """Client for show comments operations."""

    @handle_api_errors
    async def get_show_comments(
        self,
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = 1,
        sort: str = "newest",
    ) -> list[dict[str, Any]]:
        """Get comments for a show.

        Args:
            show_id: The Trakt show ID
            limit: Maximum number of comments to return
            page: Page number for pagination
            sort: Sort order for comments

        Returns:
            List of show comments data
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_show"]
            .replace(":id", show_id)
            .replace(":sort", sort)
        )
        return await self._make_list_request(
            endpoint, params={"limit": limit, "page": page}
        )
