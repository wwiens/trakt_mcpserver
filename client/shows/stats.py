"""Show statistics functionality (favorited, played, watched)."""

from typing import Literal, overload

from config.api import DEFAULT_FETCH_ALL_LIMIT, DEFAULT_LIMIT, DEFAULT_MAX_PAGES
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
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[FavoritedShowWrapper]: ...

    @overload
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[FavoritedShowWrapper]: ...

    @handle_api_errors
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[FavoritedShowWrapper] | PaginatedResponse[FavoritedShowWrapper]:
        """Get favorited shows from Trakt.

        Args:
            limit: Maximum total items to return when page is None,
                or items per page when page is specified.
            period: Time period for favorited shows
            page: Page number. If None, returns up to 'limit' total items.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' favorited shows
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # limit=0 means fetch all (up to safety cap)
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_favorited"],
                response_type=FavoritedShowWrapper,
                params={"limit": limit if limit > 0 else 100, "period": period},
                max_pages=max_pages,
                max_items=limit if limit > 0 else DEFAULT_FETCH_ALL_LIMIT,
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
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[PlayedShowWrapper]: ...

    @overload
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[PlayedShowWrapper]: ...

    @handle_api_errors
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[PlayedShowWrapper] | PaginatedResponse[PlayedShowWrapper]:
        """Get played shows from Trakt.

        Args:
            limit: Maximum total items to return when page is None,
                or items per page when page is specified.
            period: Time period for played shows
            page: Page number. If None, returns up to 'limit' total items.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' played shows
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # limit=0 means fetch all (up to safety cap)
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_played"],
                response_type=PlayedShowWrapper,
                params={"limit": limit if limit > 0 else 100, "period": period},
                max_pages=max_pages,
                max_items=limit if limit > 0 else DEFAULT_FETCH_ALL_LIMIT,
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
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[WatchedShowWrapper]: ...

    @overload
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[WatchedShowWrapper]: ...

    @handle_api_errors
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[WatchedShowWrapper] | PaginatedResponse[WatchedShowWrapper]:
        """Get watched shows from Trakt.

        Args:
            limit: Maximum total items to return when page is None,
                or items per page when page is specified.
            period: Time period for watched shows
            page: Page number. If None, returns up to 'limit' total items.
            max_pages: Maximum pages to fetch (safety guard for auto-pagination)

        Returns:
            If page is None: List of up to 'limit' watched shows
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # limit=0 means fetch all (up to safety cap)
            return await self.auto_paginate(
                TRAKT_ENDPOINTS["shows_watched"],
                response_type=WatchedShowWrapper,
                params={"limit": limit if limit > 0 else 100, "period": period},
                max_pages=max_pages,
                max_items=limit if limit > 0 else DEFAULT_FETCH_ALL_LIMIT,
            )

        # Single page with metadata
        return await self._make_paginated_request(
            TRAKT_ENDPOINTS["shows_watched"],
            response_type=WatchedShowWrapper,
            params={"page": page, "limit": limit, "period": period},
        )
