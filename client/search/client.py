"""Search client for searching shows and movies."""

from typing import Literal, overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import SearchResult
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SearchClient(BaseClient):
    """Client for handling search operations."""

    async def _search(
        self,
        kind: Literal["show", "movie"],
        query: str,
        limit: int,
        page: int | None,
        max_pages: int,
    ) -> list[SearchResult] | PaginatedResponse[SearchResult]:
        """Private helper for search operations.

        Args:
            kind: Type of content to search ("show" or "movie")
            query: Search query string

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = f"{TRAKT_ENDPOINTS['search']}/{kind}"

        return await self._fetch_paginated(
            endpoint,
            response_type=SearchResult,
            params={"query": query},
            page=page,
            limit=limit,
            max_pages=max_pages,
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

        See ``BaseClient._fetch_paginated`` for pagination semantics.
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

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        return await self._search("movie", query, limit, page, max_pages)
