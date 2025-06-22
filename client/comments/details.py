"""Comment details functionality."""

from typing import Any

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class CommentDetailsClient(BaseClient):
    """Client for comment details operations."""

    @handle_api_errors
    async def get_comment(self, comment_id: str) -> dict[str, Any]:
        """Get a specific comment.

        Args:
            comment_id: The Trakt comment ID

        Returns:
            Comment details data
        """
        endpoint = TRAKT_ENDPOINTS["comment"].replace(":id", comment_id)
        return await self._make_dict_request(endpoint)

    @handle_api_errors
    async def get_comment_replies(
        self,
        comment_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = 1,
        sort: str = "newest",
    ) -> list[dict[str, Any]]:
        """Get replies for a comment.

        Args:
            comment_id: The Trakt comment ID
            limit: Maximum number of replies to return
            page: Page number for pagination
            sort: Sort order for replies

        Returns:
            List of comment replies data
        """
        endpoint = (
            TRAKT_ENDPOINTS["comment_replies"]
            .replace(":id", comment_id)
            .replace(":sort", sort)
        )
        return await self._make_list_request(
            endpoint, params={"limit": limit, "page": page}
        )
