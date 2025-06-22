"""Tests for comment tools in the server.comments.tools module."""

import asyncio
from typing import Any
from unittest.mock import patch

import pytest

from server.comments.tools import (
    fetch_comment,
    fetch_comment_replies,
    fetch_episode_comments,
    fetch_movie_comments,
    fetch_season_comments,
    fetch_show_comments,
)


@pytest.mark.asyncio
async def test_fetch_movie_comments():
    """Test fetching movie comments."""
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This movie was groundbreaking!",
            "spoiler": False,
            "review": False,
            "replies": 3,
            "likes": 15,
            "id": "123",
        }
    ]

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_movie_comments.return_value = comments_future

        result = await fetch_movie_comments(movie_id="1", limit=5)

        assert "Movie ID: 1" in result
        assert "user1" in result
        assert "This movie was groundbreaking!" in result

        mock_client.get_movie_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_show_comments():
    """Test fetching show comments."""
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This show was amazing!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123",
        }
    ]

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_show_comments.return_value = comments_future

        result = await fetch_show_comments(show_id="1", limit=5)

        assert "Show ID: 1" in result
        assert "user1" in result
        assert "This show was amazing!" in result

        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_season_comments():
    """Test fetching season comments."""
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This season was amazing!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123",
        }
    ]

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_season_comments.return_value = comments_future

        result = await fetch_season_comments(show_id="1", season=1, limit=5)

        assert "Show ID: 1 - Season 1" in result
        assert "user1" in result
        assert "This season was amazing!" in result

        mock_client.get_season_comments.assert_called_once_with(
            "1", 1, limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_episode_comments():
    """Test fetching episode comments."""
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This episode was incredible!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123",
        }
    ]

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_episode_comments.return_value = comments_future

        result = await fetch_episode_comments(show_id="1", season=1, episode=1, limit=5)

        assert "Show ID: 1 - S01E01" in result
        assert "user1" in result
        assert "This episode was incredible!" in result

        mock_client.get_episode_comments.assert_called_once_with(
            "1", 1, 1, limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_comment():
    """Test fetching a specific comment."""
    sample_comment = {
        "user": {"username": "user1"},
        "created_at": "2023-01-15T20:30:00Z",
        "comment": "This is my comment!",
        "spoiler": False,
        "review": False,
        "replies": 2,
        "likes": 10,
        "id": "123",
    }

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_comment)
        mock_client.get_comment.return_value = future

        result = await fetch_comment(comment_id="123")

        assert "# Comment by user1" in result
        assert "This is my comment!" in result

        mock_client.get_comment.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_fetch_comment_replies():
    """Test fetching comment replies."""
    sample_comment = {
        "user": {"username": "user1"},
        "created_at": "2023-01-15T20:30:00Z",
        "comment": "This is my comment!",
        "spoiler": False,
        "review": False,
        "replies": 2,
        "likes": 10,
        "id": "123",
    }

    sample_replies = [
        {
            "user": {"username": "user2"},
            "created_at": "2023-01-16T10:15:00Z",
            "comment": "I agree with you!",
            "spoiler": False,
            "review": False,
            "id": "124",
        }
    ]

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comment_future: asyncio.Future[Any] = asyncio.Future()
        comment_future.set_result(sample_comment)
        mock_client.get_comment.return_value = comment_future

        replies_future: asyncio.Future[Any] = asyncio.Future()
        replies_future.set_result(sample_replies)
        mock_client.get_comment_replies.return_value = replies_future

        result = await fetch_comment_replies(comment_id="123", limit=5)

        assert "# Comment by user1" in result
        assert "This is my comment!" in result
        assert "## Replies" in result
        assert "user2" in result
        assert "I agree with you!" in result

        mock_client.get_comment.assert_called_once_with("123")
        mock_client.get_comment_replies.assert_called_once_with(
            "123", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_movie_comments_error_handling():
    """Test error handling for movie comments."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result("Error: Movie comments not found.")
        mock_client.get_movie_comments.return_value = comments_future

        result = await fetch_movie_comments(movie_id="123")

        assert (
            "Error fetching comments for Movie ID: 123: Error: Movie comments not found."
            in result
        )
        mock_client.get_movie_comments.assert_called_once_with(
            "123", limit=10, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_show_comments_error_handling():
    """Test error handling for show comments."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result("Error: Show comments not found.")
        mock_client.get_show_comments.return_value = comments_future

        result = await fetch_show_comments(show_id="123")

        assert (
            "Error fetching comments for Show ID: 123: Error: Show comments not found."
            in result
        )
        mock_client.get_show_comments.assert_called_once_with(
            "123", limit=10, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_season_comments_error_handling():
    """Test error handling for season comments."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result("Error: Season comments not found.")
        mock_client.get_season_comments.return_value = comments_future

        result = await fetch_season_comments(show_id="1", season=1)

        assert (
            "Error fetching comments for Show ID: 1 - Season 1: Error: Season comments not found."
            in result
        )
        mock_client.get_season_comments.assert_called_once_with(
            "1", 1, limit=10, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_episode_comments_error_handling():
    """Test error handling for episode comments."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result("Error: Episode comments not found.")
        mock_client.get_episode_comments.return_value = comments_future

        result = await fetch_episode_comments(show_id="1", season=1, episode=1)

        assert (
            "Error fetching comments for Show ID: 1 - S01E01: Error: Episode comments not found."
            in result
        )
        mock_client.get_episode_comments.assert_called_once_with(
            "1", 1, 1, limit=10, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_comment_string_error_handling():
    """Test fetching a comment with a string error response."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("Error: The requested comment was not found.")
        mock_client.get_comment.return_value = future

        result = await fetch_comment(comment_id="123")

        assert (
            "Error fetching comment 123: Error: The requested comment was not found."
            in result
        )

        mock_client.get_comment.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_fetch_comment_replies_string_error_handling():
    """Test fetching comment replies with a string error response."""
    sample_comment = {
        "user": {"username": "user1"},
        "created_at": "2023-01-15T20:30:00Z",
        "comment": "This is my comment!",
        "spoiler": False,
        "review": False,
        "replies": 2,
        "likes": 10,
        "id": "123",
    }

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comment_future: asyncio.Future[Any] = asyncio.Future()
        comment_future.set_result(sample_comment)
        mock_client.get_comment.return_value = comment_future

        replies_future: asyncio.Future[Any] = asyncio.Future()
        replies_future.set_result("Error: Unable to fetch replies.")
        mock_client.get_comment_replies.return_value = replies_future

        result = await fetch_comment_replies(comment_id="123", limit=5)

        assert (
            "Error fetching comment replies for 123: Error: Unable to fetch replies."
            in result
        )

        mock_client.get_comment.assert_called_once_with("123")
        mock_client.get_comment_replies.assert_called_once_with(
            "123", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_comment_with_exception():
    """Test comment fetching with exception handling."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_comment.side_effect = Exception("Network error")

        result = await fetch_comment(comment_id="123")

        assert "Error fetching comment 123: Network error" in result
        mock_client.get_comment.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_fetch_comment_replies_with_exception():
    """Test comment replies fetching with exception handling."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_comment.side_effect = Exception("Network error")

        result = await fetch_comment_replies(comment_id="123")

        assert "Error fetching comment replies for 123: Network error" in result
        mock_client.get_comment.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_fetch_movie_comments_with_spoilers():
    """Test fetching movie comments with spoilers enabled."""
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "Neo is the one!",
            "spoiler": True,
            "review": False,
            "replies": 0,
            "likes": 5,
            "id": "123",
        }
    ]

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_movie_comments.return_value = comments_future

        result = await fetch_movie_comments(movie_id="1", show_spoilers=True)

        assert "Movie ID: 1" in result
        assert "user1" in result
        # When show_spoilers=True, spoiler content should be visible
        assert "Neo is the one!" in result

        mock_client.get_movie_comments.assert_called_once_with(
            "1", limit=10, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_show_comments_with_different_sort():
    """Test fetching show comments with different sort option."""
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This show was amazing!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123",
        }
    ]

    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_show_comments.return_value = comments_future

        result = await fetch_show_comments(show_id="1", sort="likes")

        assert "Show ID: 1" in result
        assert "user1" in result
        assert "This show was amazing!" in result

        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=10, sort="likes"
        )
