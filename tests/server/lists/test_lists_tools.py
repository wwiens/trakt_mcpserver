import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.lists.tools import (
    fetch_list_items,
    fetch_popular_lists,
    fetch_trending_lists,
)


def _future(result: Any) -> "asyncio.Future[Any]":
    future: asyncio.Future[Any] = asyncio.Future()
    future.set_result(result)
    return future


@pytest.mark.asyncio
async def test_fetch_list_items():
    sample_items = [
        {
            "rank": 1,
            "id": 101,
            "listed_at": "2015-01-01T00:00:00.000Z",
            "type": "movie",
            "movie": {"title": "Zodiac", "year": 2007, "ids": {"trakt": 1}},
        },
        {
            "rank": 2,
            "id": 102,
            "listed_at": "2015-01-01T00:00:00.000Z",
            "type": "movie",
            "movie": {"title": "Identity", "year": 2003, "ids": {"trakt": 2}},
        },
    ]

    with patch("server.lists.tools.ListsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_list_items.return_value = _future(sample_items)

        result = await fetch_list_items(
            list_owner="majeed_pk", list_id="psychological-thrillers"
        )

        assert "# Items in majeed_pk/psychological-thrillers" in result
        assert "Zodiac (2007)" in result
        assert "Identity (2003)" in result
        assert "2 item(s)" in result

        mock_client.get_list_items.assert_called_once_with(
            "majeed_pk", "psychological-thrillers", item_type="all"
        )


@pytest.mark.asyncio
async def test_fetch_list_items_filters_by_type():
    with patch("server.lists.tools.ListsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_list_items.return_value = _future([])

        result = await fetch_list_items(
            list_owner="majeed_pk",
            list_id="psychological-thrillers",
            item_type="shows",
        )

        assert "This list has no items." in result
        mock_client.get_list_items.assert_called_once_with(
            "majeed_pk", "psychological-thrillers", item_type="shows"
        )


@pytest.mark.asyncio
async def test_fetch_trending_lists():
    sample_lists = [
        {
            "like_count": 110,
            "comment_count": 6,
            "list": {
                "name": "IMDB: Top Rated Movies",
                "description": "Top 250 movies.",
                "item_count": 250,
                "likes": 4899,
                "user": {"username": "justin"},
            },
        }
    ]

    with patch("server.lists.tools.ListsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_trending_lists.return_value = _future(sample_lists)

        result = await fetch_trending_lists(limit=5)

        assert "# Trending Lists on Trakt" in result
        assert "IMDB: Top Rated Movies" in result
        assert "justin" in result
        assert "250 items" in result

        mock_client.get_trending_lists.assert_called_once_with(limit=5, page=None)


@pytest.mark.asyncio
async def test_fetch_popular_lists():
    sample_lists = [
        {
            "like_count": 90,
            "comment_count": 2,
            "list": {
                "name": "Best Sci-Fi",
                "description": "Great science fiction.",
                "item_count": 42,
                "likes": 321,
                "user": {"username": "filmfan"},
            },
        }
    ]

    with patch("server.lists.tools.ListsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_popular_lists.return_value = _future(sample_lists)

        result = await fetch_popular_lists()

        assert "# Popular Lists on Trakt" in result
        assert "Best Sci-Fi" in result
        assert "filmfan" in result
        assert "42 items" in result

        mock_client.get_popular_lists.assert_called_once_with(limit=10, page=None)
