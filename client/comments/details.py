"""Comment details functionality."""

from typing import overload
from urllib.parse import quote

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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
        endpoint = TRAKT_ENDPOINTS["comment"].replace(":id", quote(comment_id, safe=""))
        return await self._make_typed_request(endpoint, response_type=CommentResponse)

    @overload
    async def get_comment_replies(
        self,
        comment_id: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[CommentResponse]: ...

    @overload
    async def get_comment_replies(
        self,
        comment_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[CommentResponse]: ...

    @handle_api_errors
    async def get_comment_replies(
        self,
        comment_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get replies for a comment.

        Args:
            comment_id: The Trakt comment ID

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = TRAKT_ENDPOINTS["comment_replies"].replace(
            ":id", quote(comment_id, safe="")
        )

        return await self._fetch_paginated(
            endpoint,
            response_type=CommentResponse,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
