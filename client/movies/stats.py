"""Movie statistics functionality (favorited, played, watched)."""

from typing import Literal, overload

from config.api import DEFAULT_LIMIT
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
        max_pages: int = 100,
    ) -> list[FavoritedMovieWrapper]: ...

    @overload
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
    ) -> PaginatedResponse[FavoritedMovieWrapper]: ...

    @handle_api_errors
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = 100,
    ) -> list[FavoritedMovieWrapper] | PaginatedResponse[FavoritedMovieWrapper]:
        """Get favorited movies from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for favorited movies
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all favorited movies across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["movies_favorited"],
                response_type=FavoritedMovieWrapper,
                params={"limit": limit, "period": period},
                max_pages=max_pages,
            )

        # Single page with metadata
        return await self._make_paginated_request(
            TRAKT_ENDPOINTS["movies_favorited"],
            response_type=FavoritedMovieWrapper,
            params={"page": page, "limit": limit, "period": period},
        )

    @overload
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: None = None,
        max_pages: int = 100,
    ) -> list[PlayedMovieWrapper]: ...

    @overload
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
    ) -> PaginatedResponse[PlayedMovieWrapper]: ...

    @handle_api_errors
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = 100,
    ) -> list[PlayedMovieWrapper] | PaginatedResponse[PlayedMovieWrapper]:
        """Get played movies from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for played movies
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all played movies across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["movies_played"],
                response_type=PlayedMovieWrapper,
                params={"limit": limit, "period": period},
                max_pages=max_pages,
            )

        # Single page with metadata
        return await self._make_paginated_request(
            TRAKT_ENDPOINTS["movies_played"],
            response_type=PlayedMovieWrapper,
            params={"page": page, "limit": limit, "period": period},
        )

    @overload
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: None = None,
        max_pages: int = 100,
    ) -> list[WatchedMovieWrapper]: ...

    @overload
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
    ) -> PaginatedResponse[WatchedMovieWrapper]: ...

    @handle_api_errors
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = 100,
    ) -> list[WatchedMovieWrapper] | PaginatedResponse[WatchedMovieWrapper]:
        """Get watched movies from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for watched movies
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all watched movies across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["movies_watched"],
                response_type=WatchedMovieWrapper,
                params={"limit": limit, "period": period},
                max_pages=max_pages,
            )

        # Single page with metadata
        return await self._make_paginated_request(
            TRAKT_ENDPOINTS["movies_watched"],
            response_type=WatchedMovieWrapper,
            params={"page": page, "limit": limit, "period": period},
        )
