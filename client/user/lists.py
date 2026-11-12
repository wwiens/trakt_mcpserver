"""Authenticated personal-list API operations."""

from client.auth import AuthClient
from client.endpoints import build_endpoint
from models.sync.watchlist import SyncWatchlistSummary, TraktSyncWatchlistRequest
from models.user.lists import CreateUserList, UpdateUserList, UserList
from utils.api.error_types import AuthenticationRequiredError
from utils.api.errors import handle_api_errors


class UserListsClient(AuthClient):
    """Manage lists owned by the authenticated user, never another user."""

    async def _require_list_auth(self) -> None:
        if not await self.ensure_authenticated():
            raise AuthenticationRequiredError(action="manage your personal lists")

    @handle_api_errors
    async def get_user_lists(self) -> list[UserList]:
        """Fetch the authenticated user's personal list metadata."""
        await self._require_list_auth()
        return await self.auto_paginate(
            build_endpoint("user_lists", id="me"), response_type=UserList
        )

    @handle_api_errors
    async def create_user_list(self, request: CreateUserList) -> UserList:
        """Create a list (201 Created)."""
        await self._require_list_auth()
        return await self._post_typed_request(
            build_endpoint("user_lists", id="me"),
            request.model_dump(mode="json", exclude_none=True),
            response_type=UserList,
        )

    @handle_api_errors
    async def update_user_list(self, list_id: str, request: UpdateUserList) -> UserList:
        """Update only supplied settings (200 OK)."""
        await self._require_list_auth()
        result = await self._make_request(
            "PUT",
            build_endpoint("user_list", id="me", list_id=list_id),
            data=request.model_dump(mode="json", exclude_none=True),
        )
        return UserList.model_validate(result)

    @handle_api_errors
    async def delete_user_list(self, list_id: str) -> None:
        """Delete a list and its contents (204 No Content)."""
        await self._require_list_auth()
        await self._delete_request(
            build_endpoint("user_list", id="me", list_id=list_id)
        )

    @handle_api_errors
    async def add_user_list_items(
        self, list_id: str, request: TraktSyncWatchlistRequest
    ) -> SyncWatchlistSummary:
        """Add items, including optional VIP notes (201 Created)."""
        await self._require_list_auth()
        return await self._post_typed_request(
            build_endpoint("user_list_items", id="me", list_id=list_id),
            request.model_dump(mode="json", exclude_none=True),
            response_type=SyncWatchlistSummary,
        )

    @handle_api_errors
    async def remove_user_list_items(
        self, list_id: str, request: TraktSyncWatchlistRequest
    ) -> SyncWatchlistSummary:
        """Remove items (200 OK), preserving deleted and not-found counts."""
        await self._require_list_auth()
        return await self._post_typed_request(
            build_endpoint("user_list_items_remove", id="me", list_id=list_id),
            request.model_dump(mode="json", exclude_none=True),
            response_type=SyncWatchlistSummary,
        )
