"""Popular shows functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import ShowResponse
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class PopularShowsClient(BaseClient):
    """Client for popular shows operations."""

    @overload
    async def get_popular_shows(
        self, limit: int = DEFAULT_LIMIT, page: None = None, max_pages: int = 100
    ) -> list[ShowResponse]: ...

    @overload
    async def get_popular_shows(
        self, limit: int = DEFAULT_LIMIT, page: int = ...
    ) -> PaginatedResponse[ShowResponse]: ...

    @handle_api_errors
    async def get_popular_shows(
        self, limit: int = DEFAULT_LIMIT, page: int | None = None, max_pages: int = 100
    ) -> list[ShowResponse] | PaginatedResponse[ShowResponse]:
        """Get popular shows from Trakt.

        Args:
            limit: Items per page (default: DEFAULT_LIMIT)
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all popular shows across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_popular"],
                response_type=ShowResponse,
                params={"limit": limit},
                max_pages=max_pages,
            )
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["shows_popular"],
                response_type=ShowResponse,
                params={"page": page, "limit": limit},
            )
