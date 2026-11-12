"""Personal user-list endpoint registration and safe interpolation."""

import pytest

from client.endpoints import build_endpoint
from config.endpoints import TRAKT_ENDPOINTS, EndpointKey
from config.endpoints.user import USER_ENDPOINTS


@pytest.mark.parametrize(
    ("key", "suffix"),
    [
        ("user_lists", ""),
        ("user_list", "/:list_id"),
        ("user_list_items", "/:list_id/items"),
        ("user_list_items_remove", "/:list_id/items/remove"),
        ("user_list_items_type", "/:list_id/items/:type"),
    ],
)
def test_user_list_registry(key: EndpointKey, suffix: str) -> None:
    assert USER_ENDPOINTS[key] == "/users/:id/lists" + suffix
    assert TRAKT_ENDPOINTS[key] == USER_ENDPOINTS[key]


@pytest.mark.parametrize("list_id", [42, "weekend", "spaces /?#"])
def test_list_identifier_encoding(list_id: str | int) -> None:
    expected = "spaces%20%2F%3F%23" if list_id == "spaces /?#" else str(list_id)
    assert build_endpoint("user_list", id="me", list_id=list_id) == (
        "/users/me/lists/" + expected
    )


@pytest.mark.parametrize("item_type", ["movie", "show", "season", "episode", "person"])
def test_personal_list_item_type_endpoint(item_type: str) -> None:
    assert (
        build_endpoint(
            "user_list_items_type", id="me", list_id="private /?#", type=item_type
        )
        == "/users/me/lists/private%20%2F%3F%23/items/" + item_type
    )
