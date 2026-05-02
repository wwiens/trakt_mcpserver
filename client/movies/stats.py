"""Movie statistics functionality (favorited, played, watched)."""

from typing import Literal, overload

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import FavoritedMovieWrapper, PlayedMovieWrapper, WatchedMovieWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient

StatsPeriod = Literal["daily", "weekly", "monthly", "yearly", "all"]


class MovieStatsClient(BaseClient):
    """Client for movie statistics operations."""

    @overload
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[FavoritedMovieWrapper]: ...

    @overload
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[FavoritedMovieWrapper]: ...

    @handle_api_errors
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[FavoritedMovieWrapper] | PaginatedResponse[FavoritedMovieWrapper]:
        """Get favorited movies from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics.
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
        period: StatsPeriod = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[PlayedMovieWrapper]: ...

    @overload
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[PlayedMovieWrapper]: ...

    @handle_api_errors
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[PlayedMovieWrapper] | PaginatedResponse[PlayedMovieWrapper]:
        """Get played movies from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics.
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
        period: StatsPeriod = "weekly",
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[WatchedMovieWrapper]: ...

    @overload
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[WatchedMovieWrapper]: ...

    @handle_api_errors
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: StatsPeriod = "weekly",
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[WatchedMovieWrapper] | PaginatedResponse[WatchedMovieWrapper]:
        """Get watched movies from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = TRAKT_ENDPOINTS["movies_watched"].replace(":period", period)
        return await self._fetch_paginated(
            endpoint,
            response_type=WatchedMovieWrapper,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
