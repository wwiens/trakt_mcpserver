"""Related shows functionality."""

from typing import overload
from urllib.parse import quote

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES, effective_limit
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
            show_id: Show identifier (Trakt ID, Trakt slug, IMDB, TMDB, or TVDB ID)
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' related shows
            If page specified: Paginated response with metadata for that page
        """
        endpoint = TRAKT_ENDPOINTS["shows_related"].replace(
            ":id", quote(show_id, safe="")
        )

        if page is None:
            eff = effective_limit(limit)
            return await self.auto_paginate(
                endpoint,
                response_type=ShowResponse,
                params={"limit": eff.api_limit},
                max_pages=max_pages,
                max_items=eff.max_items,
            )
        else:
            if page < 1:
                raise ValueError(f"page must be >= 1, got {page}")
            if limit < 1:
                raise ValueError(f"limit must be >= 1, got {limit}")
            return await self._make_paginated_request(
                endpoint,
                response_type=ShowResponse,
                params={"page": page, "limit": limit},
            )
