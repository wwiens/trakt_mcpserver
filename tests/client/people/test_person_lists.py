from unittest.mock import MagicMock

import pytest

from client.people import PeopleClient


@pytest.mark.asyncio
async def test_get_person_lists(
    trakt_env: None, patched_httpx_client: MagicMock
) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "name": "Incredible Thoughts",
            "description": "How could my brain conceive them?",
            "privacy": "public",
            "type": "personal",
            "display_numbers": True,
            "allow_comments": True,
            "sort_by": "rank",
            "sort_how": "asc",
            "created_at": "2014-10-11T17:00:54.000Z",
            "updated_at": "2014-10-11T17:00:54.000Z",
            "item_count": 50,
            "comment_count": 10,
            "likes": 99,
            "ids": {"trakt": 1337, "slug": "incredible-thoughts"},
            "user": {
                "username": "justin",
                "private": False,
                "name": "Justin Nemeth",
                "vip": True,
                "ids": {"slug": "justin"},
            },
        }
    ]
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    patched_httpx_client.get.return_value = mock_response

    client = PeopleClient()
    result = await client.get_person_lists("bryan-cranston", page=1)
    assert not isinstance(result, str)

    assert len(result) == 1
    assert result[0]["name"] == "Incredible Thoughts"
    assert result[0]["likes"] == 99

    patched_httpx_client.get.assert_called_once()
    call_args = patched_httpx_client.get.call_args
    assert "/people/bryan-cranston/lists/all/popular" in call_args[0][0]


@pytest.mark.asyncio
async def test_get_person_lists_invalid_type(
    trakt_env: None, patched_httpx_client: MagicMock
) -> None:
    client = PeopleClient()
    with pytest.raises(ValueError, match="Invalid list_type"):
        await client.get_person_lists("bryan-cranston", list_type="invalid")


@pytest.mark.asyncio
async def test_get_person_lists_invalid_sort(
    trakt_env: None, patched_httpx_client: MagicMock
) -> None:
    client = PeopleClient()
    with pytest.raises(ValueError, match="Invalid sort"):
        await client.get_person_lists("bryan-cranston", sort="invalid")
