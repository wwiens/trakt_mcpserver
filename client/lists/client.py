"""Lists functionality for community and official Trakt lists."""

from typing import Final, overload

from client.endpoints import build_endpoint
from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import ListMediaItemResponse, TrendingListResponse
from models.types.pagination import PaginatedResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient

VALID_ITEM_TYPES: Final[frozenset[str]] = frozenset(
    {"all", "movies", "shows", "seasons", "episodes", "people"}
)


class ListsClient(BaseClient):
    """Client for community and official list operations."""

    @handle_api_errors
    async def get_list_items(
        self,
        list_owner: str,
        list_id: str,
        item_type: str = "all",
    ) -> list[ListMediaItemResponse]:
        """Get the items on a user's list.

        Args:
            list_owner: Trakt username (slug) that owns the list
            list_id: Trakt list ID or slug
            item_type: Filter by type: 'all', 'movies', 'shows', 'seasons',
                'episodes', 'people'

        Returns:
            List of items on the list

        Raises:
            ValueError: If list_owner/list_id is empty or item_type is invalid
        """
        list_owner = list_owner.strip()
        list_id = list_id.strip()
        if not list_owner:
            msg = "list_owner cannot be empty"
            raise ValueError(msg)
        if not list_id:
            msg = "list_id cannot be empty"
            raise ValueError(msg)

        if item_type not in VALID_ITEM_TYPES:
            msg = (
                f"Invalid item_type '{item_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_ITEM_TYPES))}"
            )
            raise ValueError(msg)

        endpoint = build_endpoint(
            "list_items", owner=list_owner, id=list_id, type=item_type
        )
        return await self._make_typed_list_request(
            endpoint, response_type=ListMediaItemResponse
        )

    @overload
    async def get_trending_lists(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[TrendingListResponse]: ...

    @overload
    async def get_trending_lists(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[TrendingListResponse]: ...

    @handle_api_errors
    async def get_trending_lists(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[TrendingListResponse] | PaginatedResponse[TrendingListResponse]:
        """Get trending lists from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics
        (``page=None`` auto-paginates up to ``limit``; ``page=int`` returns one page).
        """
        return await self._fetch_paginated(
            TRAKT_ENDPOINTS["trending_lists"],
            response_type=TrendingListResponse,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )

    @overload
    async def get_popular_lists(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[TrendingListResponse]: ...

    @overload
    async def get_popular_lists(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[TrendingListResponse]: ...

    @handle_api_errors
    async def get_popular_lists(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[TrendingListResponse] | PaginatedResponse[TrendingListResponse]:
        """Get popular lists from Trakt.

        See ``BaseClient._fetch_paginated`` for pagination semantics
        (``page=None`` auto-paginates up to ``limit``; ``page=int`` returns one page).
        """
        return await self._fetch_paginated(
            TRAKT_ENDPOINTS["popular_lists"],
            response_type=TrendingListResponse,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
