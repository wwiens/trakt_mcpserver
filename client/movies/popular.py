"""Popular movies functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES, effective_limit
from config.endpoints import TRAKT_ENDPOINTS
from models.types import MovieResponse
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class PopularMoviesClient(BaseClient):
    """Client for popular movies operations."""

    @overload
    async def get_popular_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[MovieResponse]: ...

    @overload
    async def get_popular_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[MovieResponse]: ...

    @handle_api_errors
    async def get_popular_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[MovieResponse] | PaginatedResponse[MovieResponse]:
        """Get popular movies from Trakt.

        Args:
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' popular movies
            If page specified: Paginated response with metadata for that page

        Raises:
            RuntimeError: If auto-pagination hits max_pages limit without completing
                (only when limit > 0, not when limit=0 which is capped).
        """
        if page is None:
            api_limit, max_items = effective_limit(limit)
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["movies_popular"],
                response_type=MovieResponse,
                params={"limit": api_limit},
                max_pages=max_pages,
                max_items=max_items,
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["movies_popular"],
                response_type=MovieResponse,
                params={"page": page, "limit": limit},
            )
