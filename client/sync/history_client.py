"""Sync history functionality for Trakt."""

from typing import TYPE_CHECKING, Literal

from config.endpoints.sync import SYNC_ENDPOINTS
from models.sync.history import (
    HistoryQueryParams,
    HistorySummary,
    TraktHistoryRequest,
    WatchHistoryItem,
)
from models.types.pagination import PaginatedResponse, PaginationParams
from utils.api.error_types import AuthenticationRequiredError
from utils.api.errors import handle_api_errors

from ..auth import AuthClient

if TYPE_CHECKING:
    from models.types.common import JSONValue


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
            AuthenticationRequiredError: If not authenticated
            ValidationError: If query params are invalid (e.g., item_id without
                history_type, or start_at/end_at not valid ISO 8601 dates)
        """
        if not await self.ensure_authenticated():
            raise AuthenticationRequiredError(action="fetch watch history")

        # Validate query parameters with Pydantic model
        params = HistoryQueryParams(
            history_type=history_type,
            item_id=item_id,
            start_at=start_at,
            end_at=end_at,
        )

        # Build endpoint URL based on provided filters
        if params.history_type and params.item_id:
            endpoint = (
                SYNC_ENDPOINTS["sync_history_get"]
                .replace(":type", params.history_type)
                .replace(":item_id", params.item_id)
            )
        elif params.history_type:
            endpoint = SYNC_ENDPOINTS["sync_history_get_type"].replace(
                ":type", params.history_type
            )
        else:
            endpoint = SYNC_ENDPOINTS["sync_history_add"]

        # Build query params
        query_params: dict[str, str | int] = {}
        if params.start_at:
            query_params["start_at"] = params.start_at
        if params.end_at:
            query_params["end_at"] = params.end_at
        if pagination:
            query_params.update(pagination.to_query_params())

        return await self._make_paginated_request(
            endpoint,
            response_type=WatchHistoryItem,
            params=query_params if query_params else None,
        )

    @handle_api_errors
    async def add_to_history(self, request: TraktHistoryRequest) -> HistorySummary:
        """Add items to watch history.

        Args:
            request: History request with items to add

        Returns:
            Summary of added items with counts and any not found items

        Raises:
            AuthenticationRequiredError: If not authenticated
        """
        if not await self.ensure_authenticated():
            raise AuthenticationRequiredError(action="add items to history")

        # Convert request to dict, excluding None values
        # Use mode='json' to serialize datetime fields to ISO 8601 strings
        data: dict[str, JSONValue] = request.model_dump(mode="json", exclude_none=True)

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
            AuthenticationRequiredError: If not authenticated
        """
        if not await self.ensure_authenticated():
            raise AuthenticationRequiredError(action="remove items from history")

        # Convert request to dict, excluding None values
        # Use mode='json' to serialize datetime fields to ISO 8601 strings
        data: dict[str, JSONValue] = request.model_dump(mode="json", exclude_none=True)

        return await self._post_typed_request(
            SYNC_ENDPOINTS["sync_history_remove"],
            data,
            response_type=HistorySummary,
        )
