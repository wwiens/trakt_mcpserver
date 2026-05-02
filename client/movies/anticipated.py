"""Anticipated movies functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types.api_responses import AnticipatedMovieWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class AnticipatedMoviesClient(BaseClient):
    """Client for anticipated movies operations."""

    @overload
    async def get_anticipated_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[AnticipatedMovieWrapper]: ...

    @overload
    async def get_anticipated_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[AnticipatedMovieWrapper]: ...

    @handle_api_errors
    async def get_anticipated_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[AnticipatedMovieWrapper] | PaginatedResponse[AnticipatedMovieWrapper]:
        """Get anticipated movies from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics
        (``page=None`` auto-paginates up to ``limit``; ``page=int`` returns one page).
        """
        return await self._fetch_paginated(
            TRAKT_ENDPOINTS["movies_anticipated"],
            response_type=AnticipatedMovieWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
