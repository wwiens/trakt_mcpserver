"""Mock-HTTP coverage for authenticated personal-list operations."""

import json
from collections.abc import Awaitable
from typing import Final
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from client.user.lists import UserListsClient
from models.auth import TraktAuthToken
from models.sync.watchlist import SyncWatchlistSummary, TraktSyncWatchlistRequest
from models.types.pagination import PaginatedResponse
from models.user.lists import (
    CreateUserList,
    UpdateUserList,
    UserList,
    UserListItem,
    UserListItemType,
)
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
        case "read":
            return client.get_user_list_items("weekend")
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
    "operation", ["fetch", "create", "update", "delete", "add", "remove", "read"]
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
@pytest.mark.parametrize("operation", ["update", "delete", "add", "remove", "read"])
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "item_type", [None, "movie", "show", "season", "episode", "person"]
)
async def test_read_list_items_authenticated_http(
    item_type: UserListItemType | None, mock_auth_token: TraktAuthToken
) -> None:
    """Use OAuth and singular type paths, safely encoding the private list ID."""
    requests: list[httpx.Request] = []
    content_type = item_type or "movie"
    content: dict[str, object] = {"ids": {"trakt": 314}}
    match content_type:
        case "person":
            content["name"] = "Keanu Reeves"
        case "season":
            content["number"] = 1
        case "episode":
            content.update({"season": 1, "number": 2, "title": "Pilot"})
        case _:
            content.update({"title": "Weekend pick", "year": 1999})
    payload = {
        "rank": 1,
        "id": 9001,
        "listed_at": "2026-01-01T00:00:00Z",
        "notes": "Private note",
        "type": content_type,
        content_type: content,
    }

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[payload])

    client = UserListsClient()
    client.auth_token = mock_auth_token
    async with httpx.AsyncClient(
        base_url=client.BASE_URL, transport=httpx.MockTransport(handle)
    ) as http:
        with (
            patch.object(client, "_client", http),
            patch.object(client, "ensure_authenticated", AsyncMock(return_value=True)),
        ):
            result = await client.get_user_list_items("private /?#", item_type)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == UserListItem.model_validate(payload)
    assert len(requests) == 1
    request = requests[0]
    suffix = f"/{item_type}" if item_type else ""
    assert request.url.raw_path.split(b"?")[0].decode() == (
        "/users/me/lists/private%20%2F%3F%23/items" + suffix
    )
    assert request.headers["Authorization"] == f"Bearer {mock_auth_token.access_token}"
    assert request.url.params["limit"] == "10"
    assert request.url.params["page"] == "1"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("limit", "page", "count", "expected_pages"),
    [(2, None, 2, ["1", "2"]), (1, 2, 1, ["2"]), (0, None, 100, ["1"])],
)
async def test_read_list_items_pagination(
    limit: int, page: int | None, count: int, expected_pages: list[str]
) -> None:
    """Auto-paginate, expose one page, and retain the fetch-all safety cap."""
    pages: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        current = request.url.params["page"]
        pages.append(current)
        size = 100 if limit == 0 else 1
        payload = {
            "rank": 1,
            "id": 9001,
            "listed_at": "2026-01-01T00:00:00Z",
            "type": "movie",
            "movie": {"title": "Test", "ids": {"trakt": 314}},
        }
        return httpx.Response(
            200,
            json=[payload] * size,
            headers={
                "X-Pagination-Page": current,
                "X-Pagination-Limit": str(size),
                "X-Pagination-Page-Count": "2",
                "X-Pagination-Item-Count": str(size * 2),
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
            result = await client.get_user_list_items("weekend", limit=limit, page=page)
    assert pages == expected_pages
    if page is not None:
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == count
        assert result.pagination.current_page == page
        assert result.pagination.has_previous_page
    else:
        assert isinstance(result, list)
        assert len(result) == count
