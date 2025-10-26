"""Show statistics functionality (favorited, played, watched)."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import FavoritedShowWrapper, PlayedShowWrapper, WatchedShowWrapper
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class ShowStatsClient(BaseClient):
    """Client for show statistics operations."""

    @handle_api_errors
    async def get_favorited_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: str = "weekly",
        page: int | None = None,
    ) -> list[FavoritedShowWrapper] | PaginatedResponse[FavoritedShowWrapper]:
        """Get favorited shows from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for favorited shows
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all favorited shows across all pages
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[FavoritedShowWrapper] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    TRAKT_ENDPOINTS["shows_favorited"],
                    response_type=FavoritedShowWrapper,
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
                TRAKT_ENDPOINTS["shows_favorited"],
                response_type=FavoritedShowWrapper,
                params={"page": page, "limit": limit, "period": period},
            )

    @handle_api_errors
    async def get_played_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: str = "weekly",
        page: int | None = None,
    ) -> list[PlayedShowWrapper] | PaginatedResponse[PlayedShowWrapper]:
        """Get played shows from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for played shows
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all played shows across all pages
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[PlayedShowWrapper] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    TRAKT_ENDPOINTS["shows_played"],
                    response_type=PlayedShowWrapper,
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
                TRAKT_ENDPOINTS["shows_played"],
                response_type=PlayedShowWrapper,
                params={"page": page, "limit": limit, "period": period},
            )

    @handle_api_errors
    async def get_watched_shows(
        self,
        limit: int = DEFAULT_LIMIT,
        period: str = "weekly",
        page: int | None = None,
    ) -> list[WatchedShowWrapper] | PaginatedResponse[WatchedShowWrapper]:
        """Get watched shows from Trakt.

        Args:
            limit: Items per page (default: 10)
            period: Time period for watched shows
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all watched shows across all pages
            If page specified: Paginated response with metadata for that page
        """
        if page is None:
            # Auto-paginate: fetch all pages
            all_items: list[WatchedShowWrapper] = []
            current_page = 1

            while True:
                response = await self._make_paginated_request(
                    TRAKT_ENDPOINTS["shows_watched"],
                    response_type=WatchedShowWrapper,
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
                TRAKT_ENDPOINTS["shows_watched"],
                response_type=WatchedShowWrapper,
                params={"page": page, "limit": limit, "period": period},
            )
