"""Movie comments functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import CommentResponse
from models.types.pagination import PaginatedResponse
from models.types.sort import MovieCommentSort
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieCommentsClient(BaseClient):
    """Client for movie comments operations."""

    @overload
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        sort: MovieCommentSort = "newest",
    ) -> list[CommentResponse]: ...

    @overload
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        sort: MovieCommentSort = "newest",
    ) -> PaginatedResponse[CommentResponse]: ...

    @handle_api_errors
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: MovieCommentSort = "newest",
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
            return await self.auto_paginate(
                endpoint,
                response_type=CommentResponse,
                params={"limit": limit},
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                endpoint,
                response_type=CommentResponse,
                params={"page": page, "limit": limit},
            )
