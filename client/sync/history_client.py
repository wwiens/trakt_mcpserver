"""Sync history functionality for Trakt."""

from typing import Any, Literal

from config.endpoints.sync import SYNC_ENDPOINTS
from models.sync.history import (
    HistorySummary,
    TraktHistoryRequest,
    WatchHistoryItem,
)
from models.types.pagination import PaginatedResponse, PaginationParams
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


class SyncHistoryClient(AuthClient):
    """Client for sync history operations."""

    @handle_api_errors
    async def get_history(
        self,
        history_type: Literal["movies", "shows", "seasons", "episodes"] | None = None,
        item_id: str | None = None,
        start_at: str | None = None,
        end_at: str | None = None,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[WatchHistoryItem]:
        """Fetch watch history, optionally filtered by type and/or specific item.

        Args:
            history_type: Type of content to filter (movies, shows, seasons, episodes)
            item_id: Trakt ID for a specific item (requires history_type)
            start_at: Filter watches after this date (ISO 8601)
            end_at: Filter watches before this date (ISO 8601)
            pagination: Optional pagination parameters (page, limit)

        Returns:
            Paginated response with watch history items and pagination metadata

        Raises:
            ValueError: If not authenticated or item_id provided without history_type
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to fetch watch history")

        if item_id and not history_type:
            raise ValueError("history_type is required when specifying item_id")

        # Build the endpoint URL
        endpoint = SYNC_ENDPOINTS["sync_history_get"]

        # Replace type placeholder (empty string if not provided)
        type_part = history_type if history_type else ""
        endpoint = endpoint.replace("{type}", type_part)

        # Replace item_id placeholder (empty string if not provided)
        id_part = item_id if item_id else ""
        endpoint = endpoint.replace("{item_id}", id_part)

        # Clean up double slashes and trailing slashes
        endpoint = endpoint.replace("//", "/").rstrip("/")

        # Build query params
        params: dict[str, Any] = {}
        if start_at:
            params["start_at"] = start_at
        if end_at:
            params["end_at"] = end_at
        if pagination:
            params.update(pagination.model_dump())

        return await self._make_paginated_request(
            endpoint,
            response_type=WatchHistoryItem,
            params=params if params else None,
        )

    @handle_api_errors
    async def add_to_history(self, request: TraktHistoryRequest) -> HistorySummary:
        """Add items to watch history.

        Args:
            request: History request with items to add

        Returns:
            Summary of added items with counts and any not found items

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to add items to history")

        # Convert request to dict, excluding None values
        # Use mode='json' to serialize datetime fields to ISO 8601 strings
        data: dict[str, Any] = request.model_dump(mode="json", exclude_none=True)

        return await self._post_typed_request(
            SYNC_ENDPOINTS["sync_history_add"],
            data,
            response_type=HistorySummary,
        )

    @handle_api_errors
    async def remove_from_history(self, request: TraktHistoryRequest) -> HistorySummary:
        """Remove items from watch history.

        Args:
            request: History request with items to remove

        Returns:
            Summary of removed items with counts and any not found items

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to remove items from history")

        # Convert request to dict, excluding None values
        # Use mode='json' to serialize datetime fields to ISO 8601 strings
        data: dict[str, Any] = request.model_dump(mode="json", exclude_none=True)

        return await self._post_typed_request(
            SYNC_ENDPOINTS["sync_history_remove"],
            data,
            response_type=HistorySummary,
        )
