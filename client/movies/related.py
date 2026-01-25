"""Related movies functionality."""

from typing import overload
from urllib.parse import quote

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES, effective_limit
from config.endpoints import TRAKT_ENDPOINTS
from models.types import MovieResponse
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class RelatedMoviesClient(BaseClient):
    """Client for related movies operations."""

    @overload
    async def get_related_movies(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[MovieResponse]: ...

    @overload
    async def get_related_movies(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[MovieResponse]: ...

    @handle_api_errors
    async def get_related_movies(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[MovieResponse] | PaginatedResponse[MovieResponse]:
        """Get movies related to a specific movie.

        Args:
            movie_id: Trakt ID, Trakt slug, or IMDB ID
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' related movies
            If page specified: Paginated response with metadata for that page
        """
        endpoint = TRAKT_ENDPOINTS["movies_related"].replace(
            ":id", quote(movie_id, safe="")
        )

        if page is None:
            eff = effective_limit(limit)
            return await self.auto_paginate(
                endpoint,
                response_type=MovieResponse,
                params={"limit": eff.api_limit},
                max_pages=max_pages,
                max_items=eff.max_items,
            )
        else:
            return await self._make_paginated_request(
                endpoint,
                response_type=MovieResponse,
                params={"page": page, "limit": limit},
            )
