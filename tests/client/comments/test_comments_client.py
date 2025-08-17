import os
from unittest.mock import MagicMock, patch

import pytest

from client.comments import CommentsClient


@pytest.mark.asyncio
async def test_get_show_comments():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "123",
            "comment": "This show is amazing!",
            "spoiler": False,
            "review": False,
            "replies": 5,
            "likes": 10,
            "created_at": "2023-06-01T12:00:00Z",
            "user": {"username": "testuser"},
        },
        {
            "id": "124",
            "comment": "One of the best shows ever made!",
            "spoiler": False,
            "review": True,
            "replies": 2,
            "likes": 25,
            "created_at": "2023-06-02T15:30:00Z",
            "user": {"username": "reviewer123"},
        },
    ]
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = CommentsClient()
        result = await client.get_show_comments("1", limit=10, sort="newest")

        assert len(result) == 2
        assert result[0]["id"] == "123"
        assert result[0]["comment"] == "This show is amazing!"
        assert result[0]["user"]["username"] == "testuser"
        assert result[1]["review"] is True


@pytest.mark.asyncio
async def test_get_movie_comments():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "456",
            "comment": "Incredible movie with amazing cinematography!",
            "spoiler": False,
            "review": True,
            "replies": 8,
            "likes": 45,
            "created_at": "2023-06-03T18:45:00Z",
            "user": {"username": "cinephile"},
        }
    ]
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = CommentsClient()
        result = await client.get_movie_comments("1", limit=10, sort="likes")

        assert len(result) == 1
        assert result[0]["id"] == "456"
        assert result[0]["comment"] == "Incredible movie with amazing cinematography!"
        assert result[0]["user"]["username"] == "cinephile"
        assert result[0].get("likes") == 45


@pytest.mark.asyncio
async def test_get_comment_replies():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "789",
            "comment": "I totally agree with your review!",
            "spoiler": False,
            "review": False,
            "replies": 0,
            "likes": 3,
            "created_at": "2023-06-04T09:15:00Z",
            "user": {"username": "agreewithyou"},
        },
        {
            "id": "790",
            "comment": "Thanks for the detailed analysis!",
            "spoiler": False,
            "review": False,
            "replies": 0,
            "likes": 1,
            "created_at": "2023-06-04T10:00:00Z",
            "user": {"username": "grateful_reader"},
        },
    ]
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = CommentsClient()
        result = await client.get_comment_replies("456", limit=10, sort="newest")

        assert len(result) == 2
        assert result[0]["id"] == "789"
        assert result[0]["comment"] == "I totally agree with your review!"
        assert result[0]["user"]["username"] == "agreewithyou"
        assert result[1]["user"]["username"] == "grateful_reader"
