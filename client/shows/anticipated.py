"""Anticipated shows functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES, effective_limit
from config.endpoints import TRAKT_ENDPOINTS
from models.types.api_responses import AnticipatedShowWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class AnticipatedShowsClient(BaseClient):
    """Client for anticipated shows operations."""

    @overload
    async def get_anticipated_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[AnticipatedShowWrapper]: ...

    @overload
    async def get_anticipated_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[AnticipatedShowWrapper]: ...

    @handle_api_errors
    async def get_anticipated_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[AnticipatedShowWrapper] | PaginatedResponse[AnticipatedShowWrapper]:
        """Get anticipated shows from Trakt.

        Args:
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' anticipated shows
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            eff = effective_limit(limit)
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_anticipated"],
                response_type=AnticipatedShowWrapper,
                params={"limit": eff.api_limit},
                max_pages=max_pages,
                max_items=eff.max_items,
            )
        else:
            # Single page with metadata
            if page < 1:
                raise ValueError(f"page must be >= 1, got {page}")
            eff = effective_limit(limit)
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["shows_anticipated"],
                response_type=AnticipatedShowWrapper,
                params={"page": page, "limit": eff.api_limit},
            )
