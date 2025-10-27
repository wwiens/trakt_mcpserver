"""Season comments functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import CommentResponse
from models.types.pagination import PaginatedResponse
from models.types.sort import SeasonCommentSort
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SeasonCommentsClient(BaseClient):
    """Client for season comments operations."""

    @overload
    async def get_season_comments(
        self,
        show_id: str,
        season: int,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        sort: SeasonCommentSort = "newest",
        max_pages: int = 100,
    ) -> list[CommentResponse]: ...

    @overload
    async def get_season_comments(
        self,
        show_id: str,
        season: int,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        sort: SeasonCommentSort = "newest",
    ) -> PaginatedResponse[CommentResponse]: ...

    @handle_api_errors
    async def get_season_comments(
        self,
        show_id: str,
        season: int,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: SeasonCommentSort = "newest",
        max_pages: int = 100,
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get comments for a season.

        Args:
            show_id: The Trakt show ID
            season: Season number
            limit: Maximum number of comments to return
            page: Page number (optional). If None, returns all results via auto-pagination.
            sort: Sort order for comments
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all season comments across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_season"]
            .replace(":id", show_id)
            .replace(":season", str(season))
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
