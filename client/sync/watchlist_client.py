"""Sync watchlist functionality for Trakt."""

from typing import Any, Literal

from config.endpoints.sync import SYNC_ENDPOINTS
from models.sync.watchlist import (
    SyncWatchlistSummary,
    TraktSyncWatchlistRequest,
    TraktWatchlistItem,
)
from models.types.pagination import PaginatedResponse, PaginationParams
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


class SyncWatchlistClient(AuthClient):
    """Client for sync watchlist operations."""

    @handle_api_errors
    async def get_sync_watchlist(
        self,
        watchlist_type: Literal[
            "all", "movies", "shows", "seasons", "episodes"
        ] = "all",
        sort_by: str = "rank",
        sort_how: Literal["asc", "desc"] = "asc",
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[TraktWatchlistItem]:
        """Get user's watchlist from sync API with pagination.

        Args:
            watchlist_type: Type of watchlist items to get (all, movies, shows, seasons, episodes)
            sort_by: Field to sort by (rank, added, title, released, runtime, popularity, etc.)
            sort_how: Sort direction (asc or desc)
            pagination: Optional pagination parameters (page, limit)

        Returns:
            Paginated response with user's watchlist items and pagination metadata

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError(
                "You must be authenticated to access your personal watchlist"
            )

        # Build the endpoint URL based on parameters
        if watchlist_type == "all" and sort_by == "rank" and sort_how == "asc":
            # Use the simple endpoint for default parameters
            endpoint = SYNC_ENDPOINTS["sync_watchlist_get_all"]
        elif sort_by == "rank" and sort_how == "asc":
            # Use type-only endpoint
            endpoint = SYNC_ENDPOINTS["sync_watchlist_get_type"].replace(
                ":type", watchlist_type
            )
        else:
            # Use full endpoint with all parameters
            endpoint = (
                SYNC_ENDPOINTS["sync_watchlist_get"]
                .replace(":type", watchlist_type)
                .replace(":sort_by", sort_by)
                .replace(":sort_how", sort_how)
            )

        # Build query parameters with pagination
        params: dict[str, Any] = {}
        if pagination:
            params.update(pagination.model_dump())

        return await self._make_paginated_request(
            endpoint, response_type=TraktWatchlistItem, params=params
        )

    @handle_api_errors
    async def add_sync_watchlist(
        self, request: TraktSyncWatchlistRequest
    ) -> SyncWatchlistSummary:
        """Add items to the authenticated user's watchlist.

        Args:
            request: Watchlist items to add (can include notes for VIP users)

        Returns:
            Summary of added items with counts and any not found items

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to add items to your watchlist")

        # Convert request to dict, excluding None values
        data: dict[str, Any] = request.model_dump(exclude_none=True)

        return await self._post_typed_request(
            SYNC_ENDPOINTS["sync_watchlist_add"],
            data,
            response_type=SyncWatchlistSummary,
        )

    @handle_api_errors
    async def remove_sync_watchlist(
        self, request: TraktSyncWatchlistRequest
    ) -> SyncWatchlistSummary:
        """Remove items from the authenticated user's watchlist.

        Args:
            request: Watchlist items to remove (should not include notes, just item identification)

        Returns:
            Summary of removed items with counts and any not found items

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError(
                "You must be authenticated to remove items from your watchlist"
            )

        # Convert request to dict, excluding None values
        data: dict[str, Any] = request.model_dump(exclude_none=True)

        # Use POST method for sync watchlist removal
        return await self._post_typed_request(
            SYNC_ENDPOINTS["sync_watchlist_remove"],
            data,
            response_type=SyncWatchlistSummary,
        )
