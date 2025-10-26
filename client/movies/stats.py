"""Movie statistics functionality (favorited, played, watched)."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import FavoritedMovieWrapper, PlayedMovieWrapper, WatchedMovieWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieStatsClient(BaseClient):
    """Client for movie statistics operations."""

    @handle_api_errors
    async def get_favorited_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: str = "weekly",
        page: int | None = None,
    ) -> list[FavoritedMovieWrapper] | PaginatedResponse[FavoritedMovieWrapper]:
        """Get favorited movies from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for favorited movies
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all favorited movies across all pages
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[FavoritedMovieWrapper] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    TRAKT_ENDPOINTS["movies_favorited"],
                    response_type=FavoritedMovieWrapper,
                    params={"page": current_page, "limit": limit, "period": period},
                )

                all_items.extend(response.data)

                if not response.pagination.has_next_page:
                    break

                current_page += 1

            return all_items
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["movies_favorited"],
                response_type=FavoritedMovieWrapper,
                params={"page": page, "limit": limit, "period": period},
            )

    @handle_api_errors
    async def get_played_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: str = "weekly",
        page: int | None = None,
    ) -> list[PlayedMovieWrapper] | PaginatedResponse[PlayedMovieWrapper]:
        """Get played movies from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for played movies
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all played movies across all pages
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[PlayedMovieWrapper] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    TRAKT_ENDPOINTS["movies_played"],
                    response_type=PlayedMovieWrapper,
                    params={"page": current_page, "limit": limit, "period": period},
                )

                all_items.extend(response.data)

                if not response.pagination.has_next_page:
                    break

                current_page += 1

            return all_items
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["movies_played"],
                response_type=PlayedMovieWrapper,
                params={"page": page, "limit": limit, "period": period},
            )

    @handle_api_errors
    async def get_watched_movies(
        self,
        limit: int = DEFAULT_LIMIT,
        period: str = "weekly",
        page: int | None = None,
    ) -> list[WatchedMovieWrapper] | PaginatedResponse[WatchedMovieWrapper]:
        """Get watched movies from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for watched movies
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all watched movies across all pages
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[WatchedMovieWrapper] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    TRAKT_ENDPOINTS["movies_watched"],
                    response_type=WatchedMovieWrapper,
                    params={"page": current_page, "limit": limit, "period": period},
                )

                all_items.extend(response.data)

                if not response.pagination.has_next_page:
                    break

                current_page += 1

            return all_items
        else:
            # Single page with metadata
            return await self._make_paginated_request(
                TRAKT_ENDPOINTS["movies_watched"],
                response_type=WatchedMovieWrapper,
                params={"page": page, "limit": limit, "period": period},
            )
