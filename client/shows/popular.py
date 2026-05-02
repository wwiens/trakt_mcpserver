"""Popular shows functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import ShowResponse
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class PopularShowsClient(BaseClient):
    """Client for popular shows operations."""

    @overload
    async def get_popular_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[ShowResponse]: ...

    @overload
    async def get_popular_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[ShowResponse]: ...

    @handle_api_errors
    async def get_popular_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[ShowResponse] | PaginatedResponse[ShowResponse]:
        """Get popular shows from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics
        (``page=None`` auto-paginates up to ``limit``; ``page=int`` returns one page).
        """
        return await self._fetch_paginated(
            TRAKT_ENDPOINTS["shows_popular"],
            response_type=ShowResponse,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
