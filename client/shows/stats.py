"""Show statistics functionality (favorited, played, watched)."""

from typing import Literal, overload

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import FavoritedShowWrapper, PlayedShowWrapper, WatchedShowWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowStatsClient(BaseClient):
    """Client for show statistics operations."""

    @overload
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: None = None,
        max_pages: int = 100,
    ) -> list[FavoritedShowWrapper]: ...

    @overload
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
    ) -> PaginatedResponse[FavoritedShowWrapper]: ...

    @handle_api_errors
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = 100,
    ) -> list[FavoritedShowWrapper] | PaginatedResponse[FavoritedShowWrapper]:
        """Get favorited shows from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for favorited shows
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all favorited shows across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_favorited"],
                response_type=FavoritedShowWrapper,
                params={"limit": limit, "period": period},
                max_pages=max_pages,
            )

        # Single page with metadata
        return await self._make_paginated_request(
            TRAKT_ENDPOINTS["shows_favorited"],
            response_type=FavoritedShowWrapper,
            params={"page": page, "limit": limit, "period": period},
        )

    @overload
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: None = None,
        max_pages: int = 100,
    ) -> list[PlayedShowWrapper]: ...

    @overload
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
    ) -> PaginatedResponse[PlayedShowWrapper]: ...

    @handle_api_errors
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = 100,
    ) -> list[PlayedShowWrapper] | PaginatedResponse[PlayedShowWrapper]:
        """Get played shows from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for played shows
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all played shows across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_played"],
                response_type=PlayedShowWrapper,
                params={"limit": limit, "period": period},
                max_pages=max_pages,
            )

        # Single page with metadata
        return await self._make_paginated_request(
            TRAKT_ENDPOINTS["shows_played"],
            response_type=PlayedShowWrapper,
            params={"page": page, "limit": limit, "period": period},
        )

    @overload
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: None = None,
        max_pages: int = 100,
    ) -> list[WatchedShowWrapper]: ...

    @overload
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
    ) -> PaginatedResponse[WatchedShowWrapper]: ...

    @handle_api_errors
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = 100,
    ) -> list[WatchedShowWrapper] | PaginatedResponse[WatchedShowWrapper]:
        """Get watched shows from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for watched shows
            page: Page number (optional). If None, returns all results via auto-pagination.
            max_pages: Maximum number of pages to fetch when auto-paginating (default: 100)

        Returns:
            If page is None: List of all watched shows across all pages (up to max_pages)
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_watched"],
                response_type=WatchedShowWrapper,
                params={"limit": limit, "period": period},
                max_pages=max_pages,
            )

        # Single page with metadata
        return await self._make_paginated_request(
            TRAKT_ENDPOINTS["shows_watched"],
            response_type=WatchedShowWrapper,
            params={"page": page, "limit": limit, "period": period},
        )
