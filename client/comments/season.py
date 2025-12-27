"""Season comments functionality."""

from typing import overload
from urllib.parse import quote

from config.api import DEFAULT_FETCH_ALL_LIMIT, DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[CommentResponse]: ...

    @overload
    async def get_season_comments(
        self,
        show_id: str,
        season: int,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        sort: SeasonCommentSort = "newest",
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[CommentResponse]: ...

    @handle_api_errors
    async def get_season_comments(
        self,
        show_id: str,
        season: int,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: SeasonCommentSort = "newest",
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get comments for a season.

        Args:
            show_id: The Trakt show ID
            season: Season number
            limit: Maximum total comments when page is None,
                or comments per page when page is specified.
            page: Page number. If None, returns up to 'limit' total comments.
            sort: Sort order for comments
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' season comments
            If page specified: Paginated response with metadata for that page
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_season"]
            .replace(":id", quote(show_id, safe=""))
            .replace(":season", str(season))
            .replace(":sort", sort)
        )

        if page is None:
            # limit=0 means fetch all (up to safety cap)
            return await self.auto_paginate(
                endpoint,
                response_type=CommentResponse,
                params={"limit": limit if limit > 0 else 100},
                max_pages=max_pages,
                max_items=limit if limit > 0 else DEFAULT_FETCH_ALL_LIMIT,
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                endpoint,
                response_type=CommentResponse,
                params={"page": page, "limit": limit},
            )
