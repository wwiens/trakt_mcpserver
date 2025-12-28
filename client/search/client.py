"""Search client for searching shows and movies."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES, effective_limit
from config.endpoints import TRAKT_ENDPOINTS
from models.types import SearchResult
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SearchClient(BaseClient):
    """Client for handling search operations."""

    async def _search(
        self,
        kind: str,
        query: str,
        limit: int,
        page: int | None,
        max_pages: int,
    ) -> list[SearchResult] | PaginatedResponse[SearchResult]:
        """Private helper for search operations.

        Args:
            kind: Type of content to search ("show" or "movie")
            query: Search query string
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL results to return
                - Single page (page=N): Results per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' search results
            If page specified: Paginated response with metadata for that page

        Raises:
            RuntimeError: If auto-pagination hits max_pages limit without completing
                (only when limit > 0, not when limit=0 which is capped).
        """
        endpoint = f"{TRAKT_ENDPOINTS['search']}/{kind}"

        if page is None:
            api_limit, max_items = effective_limit(limit)
            return await self.auto_paginate(
                endpoint,
                response_type=SearchResult,
                params={"query": query, "limit": api_limit},
                max_pages=max_pages,
                max_items=max_items,
            )

        return await self._make_paginated_request(
            endpoint,
            response_type=SearchResult,
            params={"query": query, "page": page, "limit": limit},
        )

    @overload
    async def search_shows(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[SearchResult]: ...

    @overload
    async def search_shows(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[SearchResult]: ...

    @handle_api_errors
    async def search_shows(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[SearchResult] | PaginatedResponse[SearchResult]:
        """Search for shows on Trakt.

        Args:
            query: Search query string
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL results to return
                - Single page (page=N): Results per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' search results
            If page specified: Paginated response with metadata for that page

        Raises:
            RuntimeError: If auto-pagination hits max_pages limit without completing
                (only when limit > 0, not when limit=0 which is capped).
        """
        return await self._search("show", query, limit, page, max_pages)

    @overload
    async def search_movies(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[SearchResult]: ...

    @overload
    async def search_movies(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[SearchResult]: ...

    @handle_api_errors
    async def search_movies(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[SearchResult] | PaginatedResponse[SearchResult]:
        """Search for movies on Trakt.

        Args:
            query: Search query string
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL results to return
                - Single page (page=N): Results per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' search results
            If page specified: Paginated response with metadata for that page

        Raises:
            RuntimeError: If auto-pagination hits max_pages limit without completing
                (only when limit > 0, not when limit=0 which is capped).
        """
        return await self._search("movie", query, limit, page, max_pages)
