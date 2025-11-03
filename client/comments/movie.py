"""Movie comments functionality."""

from typing import overload
from urllib.parse import quote

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[CommentResponse]: ...

    @overload
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        sort: MovieCommentSort = "newest",
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[CommentResponse]: ...

    @handle_api_errors
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: MovieCommentSort = "newest",
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get comments for a movie.

        Args:
            movie_id: The Trakt movie ID
            limit: Maximum number of comments to return
            page: Page number (optional). If None, returns all results via auto-pagination.
            sort: Sort order for comments
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all movie comments across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page

        Raises:
            RuntimeError: If auto-pagination reaches max_pages without completing.
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_movie"]
            .replace(":id", quote(movie_id, safe=""))
            .replace(":sort", sort)
        )

        if page is None:
            return await self.auto_paginate(
                endpoint,
                response_type=CommentResponse,
                params={"limit": limit},
                max_pages=max_pages,
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                endpoint,
                response_type=CommentResponse,
                params={"page": page, "limit": limit},
            )
