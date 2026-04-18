"""Movie statistics functionality (favorited, played, watched)."""

from typing import Literal, overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import FavoritedMovieWrapper, PlayedMovieWrapper, WatchedMovieWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieStatsClient(BaseClient):
    """Client for movie statistics operations."""

    @overload
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[FavoritedMovieWrapper]: ...

    @overload
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[FavoritedMovieWrapper]: ...

    @handle_api_errors
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[FavoritedMovieWrapper] | PaginatedResponse[FavoritedMovieWrapper]:
        """Get favorited movies from Trakt.

        Args:
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            period: Time period for favorited movies
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' favorited movies
            If page specified: Paginated response with metadata for that page
        """
        endpoint = TRAKT_ENDPOINTS["movies_favorited"].replace(":period", period)
        return await self._fetch_paginated(
            endpoint,
            response_type=FavoritedMovieWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )

    @overload
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[PlayedMovieWrapper]: ...

    @overload
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[PlayedMovieWrapper]: ...

    @handle_api_errors
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[PlayedMovieWrapper] | PaginatedResponse[PlayedMovieWrapper]:
        """Get played movies from Trakt.

        Args:
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            period: Time period for played movies
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' played movies
            If page specified: Paginated response with metadata for that page
        """
        endpoint = TRAKT_ENDPOINTS["movies_played"].replace(":period", period)
        return await self._fetch_paginated(
            endpoint,
            response_type=PlayedMovieWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )

    @overload
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[WatchedMovieWrapper]: ...

    @overload
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[WatchedMovieWrapper]: ...

    @handle_api_errors
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[WatchedMovieWrapper] | PaginatedResponse[WatchedMovieWrapper]:
        """Get watched movies from Trakt.

        Args:
            limit: Controls result size based on pagination mode:
                - Auto-pagination (page=None): Maximum TOTAL items to return
                - Single page (page=N): Items per page in the response
                Use limit=0 with page=None to fetch all available results.
            period: Time period for watched movies
            page: Page number for single-page mode, or None for auto-pagination.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' watched movies
            If page specified: Paginated response with metadata for that page
        """
        endpoint = TRAKT_ENDPOINTS["movies_watched"].replace(":period", period)
        return await self._fetch_paginated(
            endpoint,
            response_type=WatchedMovieWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
