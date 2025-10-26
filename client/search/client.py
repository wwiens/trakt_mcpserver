"""Search client for searching shows and movies."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import SearchResult
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SearchClient(BaseClient):
    """Client for handling search operations."""

    @handle_api_errors
    async def search_shows(
        self, query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[SearchResult] | PaginatedResponse[SearchResult]:
        """Search for shows on Trakt.

        Args:
            query: Search query string
            limit: Maximum number of results to return per page
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all search results across all pages
            If page specified: Paginated response with metadata for that page
        """
        # Construct search endpoint with 'show' type filter
        search_endpoint = f"{TRAKT_ENDPOINTS['search']}/show"

        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[SearchResult] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    search_endpoint,
                    response_type=SearchResult,
                    params={"query": query, "page": current_page, "limit": limit},
                )

                all_items.extend(response.data)

                if not response.pagination.has_next_page:
                    break

                current_page += 1

            return all_items
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                search_endpoint,
                response_type=SearchResult,
                params={"query": query, "page": page, "limit": limit},
            )

    @handle_api_errors
    async def search_movies(
        self, query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[SearchResult] | PaginatedResponse[SearchResult]:
        """Search for movies on Trakt.

        Args:
            query: Search query string
            limit: Maximum number of results to return per page
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all search results across all pages
            If page specified: Paginated response with metadata for that page
        """
        search_endpoint = f"{TRAKT_ENDPOINTS['search']}/movie"

        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[SearchResult] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    search_endpoint,
                    response_type=SearchResult,
                    params={"query": query, "page": current_page, "limit": limit},
                )

                all_items.extend(response.data)

                if not response.pagination.has_next_page:
                    break

                current_page += 1

            return all_items
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                search_endpoint,
                response_type=SearchResult,
                params={"query": query, "page": page, "limit": limit},
            )
