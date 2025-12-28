"""Trending shows functionality."""

from typing import overload

from config.api import DEFAULT_FETCH_ALL_LIMIT, DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' trending shows
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # limit=0 means fetch all (up to safety cap)
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_trending"],
                response_type=TrendingWrapper,
                params={"limit": limit if limit > 0 else 100},
                max_pages=max_pages,
                max_items=limit if limit > 0 else DEFAULT_FETCH_ALL_LIMIT,
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["shows_trending"],
                response_type=TrendingWrapper,
                params={"page": page, "limit": limit},
            )
