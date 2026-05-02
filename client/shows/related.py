"""Related shows functionality."""

from typing import overload
from urllib.parse import quote

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import ShowResponse
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class RelatedShowsClient(BaseClient):
    """Client for related shows operations."""

    @overload
    async def get_related_shows(
        self,
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[ShowResponse]: ...

    @overload
    async def get_related_shows(
        self,
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[ShowResponse]: ...

    @handle_api_errors
    async def get_related_shows(
        self,
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[ShowResponse] | PaginatedResponse[ShowResponse]:
        """Get shows related to a specific show.

        Args:
            show_id: Show identifier (Trakt ID, slug, IMDB, TMDB, or TVDB ID).

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = TRAKT_ENDPOINTS["shows_related"].replace(
            ":id", quote(show_id, safe="")
        )
        return await self._fetch_paginated(
            endpoint,
            response_type=ShowResponse,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
