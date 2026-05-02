"""Popular movies functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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

        See ``BaseClient._fetch_paginated`` for pagination semantics
        (``page=None`` auto-paginates up to ``limit``; ``page=int`` returns one page).
        """
        return await self._fetch_paginated(
            TRAKT_ENDPOINTS["movies_popular"],
            response_type=MovieResponse,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
