"""Personal-list content formatting across every supported item type."""

import pytest

from models.formatters.user_lists import UserListFormatters
from models.user.lists import UserListItem


@pytest.mark.parametrize(
    ("item_type", "content", "title", "year"),
    [
        ("movie", {"title": "The Matrix", "year": 1999}, "The Matrix", 1999),
        ("show", {"title": "Breaking Bad", "year": 2008}, "Breaking Bad", 2008),
        ("season", {"number": 1}, "Breaking Bad - Season 1", 2008),
        (
            "episode",
            {"season": 1, "number": 2, "title": "Cat's in the Bag..."},
            "Breaking Bad - S01E02: Cat's in the Bag...",
            2008,
        ),
        ("person", {"name": "Keanu Reeves"}, "Keanu Reeves", None),
    ],
)
def test_personal_list_item_formatting(
    item_type: str, content: dict[str, object], title: str, year: int | None
) -> None:
    payload: dict[str, object] = {
        "rank": 4,
        "id": 9001,
        "listed_at": "2026-01-01T00:00:00Z",
        "notes": "Private note",
        "type": item_type,
        item_type: {**content, "ids": {"trakt": 314}},
    }
    if item_type in {"season", "episode"}:
        payload["show"] = {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": 1},
        }
    item = UserListItem.model_validate(payload)
    result = UserListFormatters.format_list_items([item], "weekend")
    assert f"**{title}{f' ({year})' if year else ''}**" in result
    for text in (
        "#4",
        f"Type: {item_type}",
        "Trakt ID: 314",
        "List item ID: 9001",
        "Notes: Private note",
    ):
        assert text in result


def test_list_item_with_unavailable_media() -> None:
    """Trakt permits a nullable content payload after media is unavailable."""
    item = UserListItem.model_validate(
        {
            "rank": 1,
            "id": 9001,
            "listed_at": "2026-01-01T00:00:00Z",
            "notes": None,
            "type": "movie",
            "movie": None,
        }
    )
    result = UserListFormatters.format_list_items([item], "weekend")
    assert "Unavailable item" in result
    assert "Trakt ID: N/A" in result
    assert "Notes:" not in result
