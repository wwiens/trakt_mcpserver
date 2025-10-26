"""Trending movies functionality."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import TrendingWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class TrendingMoviesClient(BaseClient):
    """Client for trending movies operations."""

    @handle_api_errors
    async def get_trending_movies(
        self, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[TrendingWrapper] | PaginatedResponse[TrendingWrapper]:
        """Get trending movies from Trakt.

        Args:
            limit: Items per page (default: 10)
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all trending movies across all pages
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[TrendingWrapper] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    TRAKT_ENDPOINTS["movies_trending"],
                    response_type=TrendingWrapper,
                    params={"page": current_page, "limit": limit},
                )

                all_items.extend(response.data)

                if not response.pagination.has_next_page:
                    break

                current_page += 1

            return all_items
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["movies_trending"],
                response_type=TrendingWrapper,
                params={"page": page, "limit": limit},
            )
