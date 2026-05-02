"""Trending movies functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import TrendingWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class TrendingMoviesClient(BaseClient):
    """Client for trending movies operations."""

    @overload
    async def get_trending_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[TrendingWrapper]: ...

    @overload
    async def get_trending_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[TrendingWrapper]: ...

    @handle_api_errors
    async def get_trending_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[TrendingWrapper] | PaginatedResponse[TrendingWrapper]:
        """Get trending movies from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics
        (``page=None`` auto-paginates up to ``limit``; ``page=int`` returns one page).
        """
        return await self._fetch_paginated(
            TRAKT_ENDPOINTS["movies_trending"],
            response_type=TrendingWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
