"""Show statistics functionality (favorited, played, watched)."""

from typing import Literal, overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import FavoritedShowWrapper, PlayedShowWrapper, WatchedShowWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient

StatsPeriod = Literal["daily", "weekly", "monthly", "yearly", "all"]


class ShowStatsClient(BaseClient):
    """Client for show statistics operations."""

    @overload
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[FavoritedShowWrapper]: ...

    @overload
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[FavoritedShowWrapper]: ...

    @handle_api_errors
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[FavoritedShowWrapper] | PaginatedResponse[FavoritedShowWrapper]:
        """Get favorited shows from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = TRAKT_ENDPOINTS["shows_favorited"].replace(":period", period)
        return await self._fetch_paginated(
            endpoint,
            response_type=FavoritedShowWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )

    @overload
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[PlayedShowWrapper]: ...

    @overload
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[PlayedShowWrapper]: ...

    @handle_api_errors
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[PlayedShowWrapper] | PaginatedResponse[PlayedShowWrapper]:
        """Get played shows from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = TRAKT_ENDPOINTS["shows_played"].replace(":period", period)
        return await self._fetch_paginated(
            endpoint,
            response_type=PlayedShowWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )

    @overload
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[WatchedShowWrapper]: ...

    @overload
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[WatchedShowWrapper]: ...

    @handle_api_errors
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[WatchedShowWrapper] | PaginatedResponse[WatchedShowWrapper]:
        """Get watched shows from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = TRAKT_ENDPOINTS["shows_watched"].replace(":period", period)
        return await self._fetch_paginated(
            endpoint,
            response_type=WatchedShowWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
