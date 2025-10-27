"""Comment details functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import CommentResponse
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class CommentDetailsClient(BaseClient):
    """Client for comment details operations."""

    @handle_api_errors
    async def get_comment(self, comment_id: str) -> CommentResponse:
        """Get a specific comment.

        Args:
            comment_id: The Trakt comment ID

        Returns:
            Comment details data
        """
        endpoint = TRAKT_ENDPOINTS["comment"].replace(":id", comment_id)
        return await self._make_typed_request(endpoint, response_type=CommentResponse)

    @overload
    async def get_comment_replies(
        self,
        comment_id: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
    ) -> list[CommentResponse]: ...

    @overload
    async def get_comment_replies(
        self,
        comment_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
    ) -> PaginatedResponse[CommentResponse]: ...

    @handle_api_errors
    async def get_comment_replies(
        self,
        comment_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get replies for a comment.

        Args:
            comment_id: The Trakt comment ID
            limit: Maximum number of replies to return
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all comment replies across all pages
            If page specified: Paginated response with metadata for that page
        """
        endpoint = TRAKT_ENDPOINTS["comment_replies"].replace(":id", comment_id)

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
