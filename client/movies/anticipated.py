"""Anticipated movies functionality."""

from typing import overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES, effective_limit
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

        Args:
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' anticipated movies
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            eff = effective_limit(limit)
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["movies_anticipated"],
                response_type=AnticipatedMovieWrapper,
                params={"limit": eff.api_limit},
                max_pages=max_pages,
                max_items=eff.max_items,
            )
        else:
            # Single page with metadata
            eff = effective_limit(limit)
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["movies_anticipated"],
                response_type=AnticipatedMovieWrapper,
                params={"page": page, "limit": eff.api_limit},
            )
