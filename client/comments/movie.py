"""Movie comments functionality."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import CommentResponse
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieCommentsClient(BaseClient):
    """Client for movie comments operations."""

    @handle_api_errors
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: str = "newest",
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get comments for a movie.

        Args:
            movie_id: The Trakt movie ID
            limit: Maximum number of comments to return
            page: Page number (optional). If None, returns all results via auto-pagination.
            sort: Sort order for comments

        Returns:
            If page is None: List of all movie comments across all pages
            If page specified: Paginated response with metadata for that page
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_movie"]
            .replace(":id", movie_id)
            .replace(":sort", sort)
        )

        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[CommentResponse] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    endpoint,
                    response_type=CommentResponse,
                    params={"page": current_page, "limit": limit},
                )

                all_items.extend(response.data)

                if not response.pagination.has_next_page:
                    break

                current_page += 1

            return all_items
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                endpoint,
                response_type=CommentResponse,
                params={"page": page, "limit": limit},
            )
