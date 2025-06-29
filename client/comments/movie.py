"""Movie comments functionality."""

from typing import Any

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieCommentsClient(BaseClient):
    """Client for movie comments operations."""

    @handle_api_errors
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = 1,
        sort: str = "newest",
    ) -> list[dict[str, Any]]:
        """Get comments for a movie.

        Args:
            movie_id: The Trakt movie ID
            limit: Maximum number of comments to return
            page: Page number for pagination
            sort: Sort order for comments

        Returns:
            List of movie comments data
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_movie"]
            .replace(":id", movie_id)
            .replace(":sort", sort)
        )
        return await self._make_list_request(
            endpoint, params={"limit": limit, "page": page}
        )
