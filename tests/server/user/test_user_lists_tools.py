"""Personal list tool formatting, validation and API error coverage."""

from typing import Final
from unittest.mock import AsyncMock, patch

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import ValidationError

from config.mcp.tools.user import USER_TOOLS
from models.sync.watchlist import SyncWatchlistSummary
from models.user.lists import UserList, UserListIds
from server.sync.watchlist_inputs import (
    UserWatchlistIdentifier,
    UserWatchlistRequestItem,
)
from server.user.lists import (
    add_user_list_items,
    create_user_list,
    delete_user_list,
    fetch_user_lists,
    register_user_list_tools,
    remove_user_list_items,
    update_user_list,
)

USER_LIST: Final[UserList] = UserList(
    name="Weekend",
    description="Watch next",
    privacy="private",
    item_count=2,
    ids=UserListIds(trakt=42, slug="weekend"),
)


@pytest.mark.asyncio
async def test_fetch_lists_metadata_and_empty() -> None:
    with patch("server.user.lists.UserListsClient") as factory:
        client = factory.return_value
        client.get_user_lists = AsyncMock(return_value=[USER_LIST])
        result = await fetch_user_lists()
        for text in ("Weekend", "42", "weekend", "private", "2", "Watch next"):
            assert text in result
        client.get_user_lists.return_value = []
        assert "no personal lists" in await fetch_user_lists()


@pytest.mark.asyncio
async def test_create_list_optional_fields() -> None:
    with patch("server.user.lists.UserListsClient") as factory:
        client = factory.return_value
        client.create_user_list = AsyncMock(return_value=USER_LIST)
        assert "Created personal list" in await create_user_list("Weekend")
        request = client.create_user_list.call_args.args[0]
        assert request.model_dump(exclude_none=True) == {"name": "Weekend"}
        await create_user_list(
            "Weekend",
            description="",
            privacy="link",
            display_numbers=False,
            allow_comments=False,
            sort_by="tmdb_rating",
            sort_how="desc",
        )
        request = client.create_user_list.call_args.args[0]
        assert request.model_dump(exclude_none=True) == {
            "name": "Weekend",
            "description": "",
            "privacy": "link",
            "display_numbers": False,
            "allow_comments": False,
            "sort_by": "tmdb_rating",
            "sort_how": "desc",
        }


@pytest.mark.asyncio
async def test_update_preserves_false_and_empty_string() -> None:
    with patch("server.user.lists.UserListsClient") as factory:
        client = factory.return_value
        client.update_user_list = AsyncMock(return_value=USER_LIST)
        result = await update_user_list(42, description="", allow_comments=False)
        assert "Updated personal list" in result
        args = client.update_user_list.call_args.args
        assert args[0] == "42"
        assert args[1].model_dump(exclude_none=True) == {
            "description": "",
            "allow_comments": False,
        }


@pytest.mark.asyncio
async def test_empty_update_rejected_before_request() -> None:
    with (
        patch("server.user.lists.UserListsClient") as factory,
        pytest.raises(ValidationError),
    ):
        await update_user_list("weekend")
    factory.assert_not_called()


@pytest.mark.asyncio
async def test_delete_list() -> None:
    with patch("server.user.lists.UserListsClient") as factory:
        client = factory.return_value
        client.delete_user_list = AsyncMock(return_value=None)
        assert "Deleted personal list: 42" in await delete_user_list(42)
        client.delete_user_list.assert_awaited_once_with("42")


@pytest.mark.asyncio
@pytest.mark.parametrize("item_type", ["movies", "shows", "seasons", "episodes"])
@pytest.mark.parametrize("remove", [False, True])
async def test_list_item_payload_and_summary(item_type: str, remove: bool) -> None:
    summary = SyncWatchlistSummary.model_validate(
        {
            "added": {item_type: 1},
            "existing": {item_type: 2},
            "deleted": {item_type: 1},
            "not_found": {item_type: [{"ids": {"trakt": 99}}]},
        }
    )
    with patch("server.user.lists.UserListsClient") as factory:
        client = factory.return_value
        client.add_user_list_items = AsyncMock(return_value=summary)
        client.remove_user_list_items = AsyncMock(return_value=summary)
        if remove:
            result = await remove_user_list_items(
                "weekend",
                item_type,  # pyright: ignore[reportArgumentType]
                [UserWatchlistIdentifier(imdb_id="tt0133093")],
            )
            mock = client.remove_user_list_items
        else:
            result = await add_user_list_items(
                "weekend",
                item_type,  # pyright: ignore[reportArgumentType]
                [UserWatchlistRequestItem(imdb_id="tt0133093", notes=" Watch soon ")],
            )
            mock = client.add_user_list_items
            assert "Already in List (2)" in result
        assert "Watchlist" not in result
        assert "weekend" in result
        assert "Successfully" in result
        assert "Items Not Found (1)" in result
        assert "trakt: 99" in result
        payload = mock.call_args.args[1].model_dump(exclude_none=True)
        expected: dict[str, object] = {"ids": {"imdb": "tt0133093"}}
        if not remove:
            expected["notes"] = "Watch soon"
        assert payload == {item_type: [expected]}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("trakt_id", "314", {"trakt": 314}),
        ("slug", "the-matrix-1999", {"slug": "the-matrix-1999"}),
        ("imdb_id", "tt0133093", {"imdb": "tt0133093"}),
        ("tmdb_id", "603", {"tmdb": 603}),
        ("tvdb_id", "81189", {"tvdb": 81189}),
    ],
)
async def test_identifiers(field: str, value: str, expected: dict[str, object]) -> None:
    with patch("server.user.lists.UserListsClient") as factory:
        client = factory.return_value
        client.add_user_list_items = AsyncMock(return_value=SyncWatchlistSummary())
        await add_user_list_items(
            "weekend",
            "movies",
            [UserWatchlistRequestItem.model_validate({field: value})],
        )
        payload = client.add_user_list_items.call_args.args[1].model_dump(
            exclude_none=True
        )
        assert payload == {"movies": [{"ids": expected}]}


@pytest.mark.asyncio
async def test_title_and_year_identification() -> None:
    with patch("server.user.lists.UserListsClient") as factory:
        client = factory.return_value
        client.remove_user_list_items = AsyncMock(return_value=SyncWatchlistSummary())
        await remove_user_list_items(
            "weekend",
            "movies",
            [UserWatchlistIdentifier(title="The Matrix", year=1999)],
        )
        payload = client.remove_user_list_items.call_args.args[1].model_dump(
            exclude_none=True
        )
        assert payload == {"movies": [{"ids": {}, "title": "The Matrix", "year": 1999}]}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation", ["fetch", "create", "update", "delete", "add", "remove"]
)
async def test_api_error_strings_are_not_formatted(operation: str) -> None:
    with (
        patch("server.user.lists.UserListsClient") as factory,
        patch("server.user.lists.UserListFormatters") as formatters,
    ):
        client = factory.return_value
        for name in (
            "get_user_lists",
            "create_user_list",
            "update_user_list",
            "delete_user_list",
            "add_user_list_items",
            "remove_user_list_items",
        ):
            setattr(client, name, AsyncMock(return_value="API error: list not found"))
        match operation:
            case "fetch":
                result = await fetch_user_lists()
            case "create":
                result = await create_user_list("Weekend")
            case "update":
                result = await update_user_list("weekend", name="Updated")
            case "delete":
                result = await delete_user_list("weekend")
            case "add":
                result = await add_user_list_items(
                    "weekend", "movies", [UserWatchlistRequestItem(trakt_id="314")]
                )
            case _:
                result = await remove_user_list_items(
                    "weekend", "movies", [UserWatchlistIdentifier(trakt_id="314")]
                )
        assert result == "# Error\n\nError accessing user_list"
        formatters.format_lists.assert_not_called()
        formatters.format_items.assert_not_called()


@pytest.mark.asyncio
async def test_registration_and_parameter_descriptions() -> None:
    mcp = FastMCP("test")
    register_user_list_tools(mcp)
    tools = await mcp.list_tools()
    names = {tool.name for tool in tools}
    assert names == USER_TOOLS - {
        "fetch_user_watched_shows",
        "fetch_user_watched_movies",
    }
    for tool in tools:
        assert tool.description is not None and "OAuth" in tool.description
        for parameter in tool.inputSchema.get("properties", {}).values():
            assert parameter.get("description")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool", "arguments"),
    [
        ("create_user_list", {"name": ""}),
        ("create_user_list", {"name": "Test", "privacy": "unknown"}),
        ("create_user_list", {"name": "Test", "sort_by": "unknown"}),
        ("update_user_list", {"list_id": "weekend", "sort_how": "down"}),
        ("update_user_list", {"list_id": "weekend"}),
        ("delete_user_list", {"list_id": ""}),
        (
            "add_user_list_items",
            {"list_id": "weekend", "item_type": "people", "items": [{"trakt_id": "1"}]},
        ),
        (
            "add_user_list_items",
            {"list_id": "weekend", "item_type": "movies", "items": []},
        ),
        (
            "remove_user_list_items",
            {
                "list_id": "weekend",
                "item_type": "movies",
                "items": [{"imdb_id": "invalid"}],
            },
        ),
        (
            "add_user_list_items",
            {
                "list_id": "weekend",
                "item_type": "movies",
                "items": [{"tmdb_id": "invalid"}],
            },
        ),
        (
            "add_user_list_items",
            {
                "list_id": "weekend",
                "item_type": "movies",
                "items": [{"title": "No year"}],
            },
        ),
    ],
)
async def test_mcp_invalid_arguments(tool: str, arguments: dict[str, object]) -> None:
    mcp = FastMCP("test")
    register_user_list_tools(mcp)
    with patch("server.user.lists.UserListsClient") as factory:
        with pytest.raises(ToolError):
            await mcp.call_tool(tool, arguments)
        factory.assert_not_called()
