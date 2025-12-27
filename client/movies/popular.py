"""Popular movies functionality."""

from typing import overload

from config.api import DEFAULT_FETCH_ALL_LIMIT, DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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
            limit: Maximum total items to return when page is None,
                or items per page when page is specified.
            page: Page number. If None, returns up to 'limit' total items.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' popular movies
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # limit=0 means fetch all (up to safety cap)
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["movies_popular"],
                response_type=MovieResponse,
                params={"limit": limit if limit > 0 else 100},
                max_pages=max_pages,
                max_items=limit if limit > 0 else DEFAULT_FETCH_ALL_LIMIT,
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["movies_popular"],
                response_type=MovieResponse,
                params={"page": page, "limit": limit},
            )
