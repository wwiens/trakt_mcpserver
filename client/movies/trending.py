"""Trending movies functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import TrendingWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class TrendingMoviesClient(BaseClient):
    """Client for trending movies operations."""

    @overload
    async def get_trending_movies(
        self, limit: int = DEFAULT_LIMIT, page: None = None, max_pages: int = 100
    ) -> list[TrendingWrapper]: ...

    @overload
    async def get_trending_movies(
        self, limit: int = DEFAULT_LIMIT, page: int = ...
    ) -> PaginatedResponse[TrendingWrapper]: ...

    @handle_api_errors
    async def get_trending_movies(
        self, limit: int = DEFAULT_LIMIT, page: int | None = None, max_pages: int = 100
    ) -> list[TrendingWrapper] | PaginatedResponse[TrendingWrapper]:
        """Get trending movies from Trakt.

        Args:
            limit: Items per page (default: DEFAULT_LIMIT)
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all trending movies across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["movies_trending"],
                response_type=TrendingWrapper,
                params={"limit": limit},
                max_pages=max_pages,
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["movies_trending"],
                response_type=TrendingWrapper,
                params={"page": page, "limit": limit},
            )
