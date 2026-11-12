"""Mock-HTTP coverage for authenticated personal-list operations."""

import json
from collections.abc import Awaitable
from typing import Final
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from client.user.lists import UserListsClient
from models.sync.watchlist import SyncWatchlistSummary, TraktSyncWatchlistRequest
from models.user.lists import CreateUserList, UpdateUserList, UserList
from utils.api.error_types import (
    AuthenticationRequiredError,
    TraktResourceNotFoundError,
)
from utils.api.errors import MCPError

LIST_DATA: Final[dict[str, object]] = {
    "name": "Weekend",
    "description": "Watch next",
    "privacy": "private",
    "item_count": 2,
    "ids": {"trakt": 42, "slug": "weekend"},
}
SUMMARY_DATA: Final[dict[str, object]] = {
    "added": {"movies": 1},
    "existing": {"movies": 1},
    "deleted": {"movies": 1},
    "not_found": {"movies": [{"ids": {"trakt": 99}}]},
    "list": {"updated_at": "2026-01-01T00:00:00.000Z", "item_count": 2},
}


def _operation(client: UserListsClient, operation: str) -> Awaitable[object]:
    request = TraktSyncWatchlistRequest.model_validate(
        {"movies": [{"ids": {"trakt": 314}, "notes": "Watch soon"}]}
    )
    match operation:
        case "fetch":
            return client.get_user_lists()
        case "create":
            return client.create_user_list(CreateUserList(name="Weekend"))
        case "update":
            return client.update_user_list(
                "weekend", UpdateUserList(allow_comments=False)
            )
        case "delete":
            return client.delete_user_list("weekend")
        case "add":
            return client.add_user_list_items("weekend", request)
        case "remove":
            return client.remove_user_list_items("weekend", request)
        case _:
            raise AssertionError(operation)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("operation", "method", "path", "status"),
    [
        ("fetch", "GET", "/users/me/lists", 200),
        ("create", "POST", "/users/me/lists", 201),
        ("update", "PUT", "/users/me/lists/weekend", 200),
        ("delete", "DELETE", "/users/me/lists/weekend", 204),
        ("add", "POST", "/users/me/lists/weekend/items", 201),
        ("remove", "POST", "/users/me/lists/weekend/items/remove", 200),
    ],
)
async def test_list_http_contract(
    operation: str, method: str, path: str, status: int
) -> None:
    """Use real request serialization and typed parsing, including empty DELETE."""
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if operation == "delete":
            return httpx.Response(status)
        payload = (
            [LIST_DATA]
            if operation == "fetch"
            else SUMMARY_DATA
            if operation in {"add", "remove"}
            else LIST_DATA
        )
        return httpx.Response(status, json=payload)

    client = UserListsClient()
    async with httpx.AsyncClient(
        base_url=client.BASE_URL, transport=httpx.MockTransport(handle)
    ) as http:
        with (
            patch.object(client, "_client", http),
            patch.object(
                client, "ensure_authenticated", AsyncMock(return_value=True)
            ) as auth,
        ):
            result = await _operation(client, operation)
    auth.assert_awaited_once()
    assert len(requests) == 1
    assert requests[0].method == method
    assert requests[0].url.path == path
    if operation == "create":
        assert json.loads(requests[0].content) == {"name": "Weekend"}
        assert isinstance(result, UserList)
    elif operation == "update":
        assert json.loads(requests[0].content) == {"allow_comments": False}
        assert isinstance(result, UserList)
    elif operation in {"add", "remove"}:
        assert json.loads(requests[0].content) == {
            "movies": [{"ids": {"trakt": 314}, "notes": "Watch soon"}]
        }
        assert isinstance(result, SyncWatchlistSummary)
        assert result.not_found.movies[0].ids is not None
        assert result.not_found.movies[0].ids.trakt == 99
    elif operation == "fetch":
        assert isinstance(result, list)
        assert result == [UserList.model_validate(LIST_DATA)]
    else:
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation", ["fetch", "create", "update", "delete", "add", "remove"]
)
async def test_lists_require_oauth(operation: str) -> None:
    """Never issue an API request for unauthenticated callers."""
    client = UserListsClient()
    with (
        patch.object(client, "ensure_authenticated", AsyncMock(return_value=False)),
        patch.object(client, "_get_client") as http,
        pytest.raises(AuthenticationRequiredError),
    ):
        await _operation(client, operation)
    http.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["update", "delete", "add", "remove"])
async def test_missing_list(operation: str) -> None:
    """Preserve the existing structured 404 error mapping."""
    await _assert_http_error(operation, 404, TraktResourceNotFoundError)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["create", "add"])
async def test_account_limit(operation: str) -> None:
    """Preserve account-limit status through the existing generic HTTP error."""
    await _assert_http_error(operation, 420, MCPError)


async def _assert_http_error(
    operation: str, status: int, error_type: type[MCPError]
) -> None:
    client = UserListsClient()

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status)

    async with httpx.AsyncClient(
        base_url=client.BASE_URL, transport=httpx.MockTransport(handler)
    ) as http:
        with (
            patch.object(client, "_client", http),
            patch.object(client, "ensure_authenticated", AsyncMock(return_value=True)),
            pytest.raises(error_type) as error,
        ):
            await _operation(client, operation)
    assert error.value.data is not None
    assert error.value.data.get("http_status") == status


@pytest.mark.asyncio
async def test_fetch_lists_includes_all_pages() -> None:
    """Do not silently omit personal lists after Trakt's first page."""
    pages: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        page = request.url.params["page"]
        pages.append(page)
        return httpx.Response(
            200,
            json=[LIST_DATA],
            headers={
                "X-Pagination-Page": page,
                "X-Pagination-Limit": "1",
                "X-Pagination-Page-Count": "2",
                "X-Pagination-Item-Count": "2",
            },
        )

    client = UserListsClient()
    async with httpx.AsyncClient(
        base_url=client.BASE_URL, transport=httpx.MockTransport(handle)
    ) as http:
        with (
            patch.object(client, "_client", http),
            patch.object(client, "ensure_authenticated", AsyncMock(return_value=True)),
        ):
            result = await client.get_user_lists()
    assert len(result) == 2
    assert pages == ["1", "2"]
