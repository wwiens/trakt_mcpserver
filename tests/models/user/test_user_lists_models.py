"""Validation of personal list settings from the Trakt OpenAPI contract."""

from typing import get_args

import pytest
from pydantic import ValidationError

from models.user.lists import (
    CreateUserList,
    ListPrivacy,
    ListSortBy,
    ListSortHow,
    UpdateUserList,
)


@pytest.mark.parametrize("privacy", get_args(ListPrivacy))
def test_list_privacy(privacy: str) -> None:
    request = CreateUserList.model_validate({"name": "Test", "privacy": privacy})
    assert request.privacy == privacy


@pytest.mark.parametrize("sort_by", get_args(ListSortBy))
def test_list_sort_fields(sort_by: str) -> None:
    request = UpdateUserList.model_validate({"sort_by": sort_by})
    assert request.sort_by == sort_by


@pytest.mark.parametrize("sort_how", get_args(ListSortHow))
def test_list_sort_direction(sort_how: str) -> None:
    request = UpdateUserList.model_validate({"sort_how": sort_how})
    assert request.sort_how == sort_how


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": ""},
        {"privacy": "unknown"},
        {"sort_by": "unknown"},
        {"sort_how": "up"},
    ],
)
def test_invalid_updates(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        UpdateUserList.model_validate(payload)


def test_create_requires_name() -> None:
    with pytest.raises(ValidationError):
        CreateUserList.model_validate({})


def test_single_field_updates_preserve_false_and_empty() -> None:
    assert UpdateUserList(allow_comments=False).model_dump(exclude_none=True) == {
        "allow_comments": False
    }
    assert UpdateUserList(description="").model_dump(exclude_none=True) == {
        "description": ""
    }
