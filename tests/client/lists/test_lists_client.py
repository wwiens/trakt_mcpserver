from typing import Any
from unittest.mock import MagicMock

import pytest

from client.lists import ListsClient

_SAMPLE_ITEMS: list[dict[str, Any]] = [
    {
        "rank": 1,
        "id": 101,
        "listed_at": "2015-01-01T00:00:00.000Z",
        "type": "movie",
        "movie": {
            "title": "Zodiac",
            "year": 2007,
            "ids": {"trakt": 1, "slug": "zodiac-2007"},
        },
    },
    {
        "rank": 2,
        "id": 102,
        "listed_at": "2015-01-01T00:00:00.000Z",
        "type": "movie",
        "movie": {
            "title": "Prisoners",
            "year": 2013,
            "ids": {"trakt": 2, "slug": "prisoners-2013"},
        },
    },
]

_SAMPLE_LISTS: list[dict[str, Any]] = [
    {
        "like_count": 110,
        "comment_count": 6,
        "list": {
            "name": "IMDB: Top Rated Movies",
            "description": "Top 250 movies as rated by IMDB voters.",
            "item_count": 250,
            "comment_count": 6,
            "likes": 4899,
            "ids": {"trakt": 2142753, "slug": "imdb-top-rated-movies"},
            "user": {"username": "justin", "private": False, "ids": {"slug": "justin"}},
        },
    }
]


def _list_response(payload: list[dict[str, Any]]) -> MagicMock:
    mock_response = MagicMock()
    mock_response.json.return_value = payload
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": str(len(payload)),
    }
    return mock_response


@pytest.mark.asyncio
async def test_get_list_items(patched_httpx_client: MagicMock) -> None:
    patched_httpx_client.get.return_value = _list_response(_SAMPLE_ITEMS)

    client = ListsClient()
    result = await client.get_list_items("majeed_pk", "psychological-thrillers")
    assert not isinstance(result, str)

    assert len(result) == 2
    first = result[0]
    assert first["type"] == "movie"
    movie = first.get("movie")
    assert movie is not None and movie["title"] == "Zodiac"

    patched_httpx_client.get.assert_called_once()
    call_args = patched_httpx_client.get.call_args
    assert "/users/majeed_pk/lists/psychological-thrillers/items/all" in call_args[0][0]


@pytest.mark.asyncio
async def test_get_list_items_filters_by_type(patched_httpx_client: MagicMock) -> None:
    patched_httpx_client.get.return_value = _list_response(_SAMPLE_ITEMS)

    client = ListsClient()
    await client.get_list_items("majeed_pk", "psychological-thrillers", "movies")

    call_args = patched_httpx_client.get.call_args
    assert (
        "/users/majeed_pk/lists/psychological-thrillers/items/movies" in call_args[0][0]
    )


@pytest.mark.asyncio
async def test_get_list_items_invalid_type(patched_httpx_client: MagicMock) -> None:
    client = ListsClient()
    with pytest.raises(ValueError, match="Invalid item_type"):
        await client.get_list_items("majeed_pk", "psychological-thrillers", "invalid")


@pytest.mark.asyncio
async def test_get_list_items_empty_owner(patched_httpx_client: MagicMock) -> None:
    client = ListsClient()
    with pytest.raises(ValueError, match="list_owner cannot be empty"):
        await client.get_list_items("  ", "psychological-thrillers")


@pytest.mark.asyncio
async def test_get_trending_lists(patched_httpx_client: MagicMock) -> None:
    patched_httpx_client.get.return_value = _list_response(_SAMPLE_LISTS)

    client = ListsClient()
    result = await client.get_trending_lists()
    assert not isinstance(result, str)

    assert len(result) == 1
    assert result[0]["list"]["name"] == "IMDB: Top Rated Movies"

    call_args = patched_httpx_client.get.call_args
    assert "/lists/trending" in call_args[0][0]


@pytest.mark.asyncio
async def test_get_popular_lists(patched_httpx_client: MagicMock) -> None:
    patched_httpx_client.get.return_value = _list_response(_SAMPLE_LISTS)

    client = ListsClient()
    result = await client.get_popular_lists()
    assert not isinstance(result, str)

    assert len(result) == 1
    assert result[0]["list"]["likes"] == 4899

    call_args = patched_httpx_client.get.call_args
    assert "/lists/popular" in call_args[0][0]
