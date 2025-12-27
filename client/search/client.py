"""Search client for searching shows and movies."""

from typing import overload

from config.api import DEFAULT_FETCH_ALL_LIMIT, DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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
            limit: Maximum total results when page is None, or per-page when specified
            page: Page number. If None, returns up to 'limit' total results.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' search results
            If page specified: Paginated response with metadata for that page
        """
        endpoint = f"{TRAKT_ENDPOINTS['search']}/{kind}"

        if page is None:
            # limit=0 means fetch all (up to safety cap)
            return await self.auto_paginate(
                endpoint,
                response_type=SearchResult,
                params={"query": query, "limit": limit if limit > 0 else 100},
                max_pages=max_pages,
                max_items=limit if limit > 0 else DEFAULT_FETCH_ALL_LIMIT,
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
            limit: Maximum total results when page is None,
                or results per page when page is specified.
            page: Page number. If None, returns up to 'limit' total results.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' search results
            If page specified: Paginated response with metadata for that page
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
            limit: Maximum total results when page is None,
                or results per page when page is specified.
            page: Page number. If None, returns up to 'limit' total results.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' search results
            If page specified: Paginated response with metadata for that page
        """
        return await self._search("movie", query, limit, page, max_pages)
