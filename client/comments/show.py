"""Show comments functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import CommentResponse
from models.types.pagination import PaginatedResponse
from models.types.sort import ShowCommentSort
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowCommentsClient(BaseClient):
    """Client for show comments operations."""

    @overload
    async def get_show_comments(
        self,
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        sort: ShowCommentSort = "newest",
        max_pages: int = 100,
    ) -> list[CommentResponse]: ...

    @overload
    async def get_show_comments(
        self,
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        sort: ShowCommentSort = "newest",
    ) -> PaginatedResponse[CommentResponse]: ...

    @handle_api_errors
    async def get_show_comments(
        self,
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: ShowCommentSort = "newest",
        max_pages: int = 100,
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get comments for a show.

        Args:
            show_id: The Trakt show ID
            limit: Maximum number of comments to return
            page: Page number (optional). If None, returns all results via auto-pagination.
            sort: Sort order for comments
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all show comments across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_show"]
            .replace(":id", show_id)
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
