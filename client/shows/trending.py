"""Trending shows functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import TrendingWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class TrendingShowsClient(BaseClient):
    """Client for trending shows operations."""

    @overload
    async def get_trending_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[TrendingWrapper]: ...

    @overload
    async def get_trending_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[TrendingWrapper]: ...

    @handle_api_errors
    async def get_trending_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[TrendingWrapper] | PaginatedResponse[TrendingWrapper]:
        """Get trending shows from Trakt.

        Args:
            limit: Items per page
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating

        Returns:
            If page is None: List of all trending shows across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page

        Raises:
            RuntimeError: If auto-pagination reaches max_pages without completing.
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_trending"],
                response_type=TrendingWrapper,
                params={"limit": limit},
                max_pages=max_pages,
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["shows_trending"],
                response_type=TrendingWrapper,
                params={"page": page, "limit": limit},
            )
