"""Season comments functionality."""

from typing import overload
from urllib.parse import quote

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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
            sort: Sort order for comments

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_season"]
            .replace(":id", quote(show_id, safe=""))
            .replace(":season", str(season))
            .replace(":sort", sort)
        )

        return await self._fetch_paginated(
            endpoint,
            response_type=CommentResponse,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
