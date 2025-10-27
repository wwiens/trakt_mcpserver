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
from utils.api.error_types import (
    TraktResourceNotFoundError,
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

    with patch("server.comments.tools.MovieCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_movie_comments.return_value = comments_future

        result = await fetch_movie_comments(movie_id="1", limit=5)

        assert "Movie ID: 1" in result
        assert "user1" in result
        assert "This movie was groundbreaking!" in result

        mock_client.get_movie_comments.assert_called_once_with(
            "1", limit=5, sort="newest", page=None
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

    with patch("server.comments.tools.ShowCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_show_comments.return_value = comments_future

        result = await fetch_show_comments(show_id="1", limit=5)

        assert "Show ID: 1" in result
        assert "user1" in result
        assert "This show was amazing!" in result

        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=5, sort="newest", page=None
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

    with patch("server.comments.tools.SeasonCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_season_comments.return_value = comments_future

        result = await fetch_season_comments(show_id="1", season=1, limit=5)

        assert "Show ID: 1 - Season 1" in result
        assert "user1" in result
        assert "This season was amazing!" in result

        mock_client.get_season_comments.assert_called_once_with(
            "1", 1, limit=5, sort="newest", page=None
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

    with patch("server.comments.tools.EpisodeCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_episode_comments.return_value = comments_future

        result = await fetch_episode_comments(show_id="1", season=1, episode=1, limit=5)

        assert "Show ID: 1 - S01E01" in result
        assert "user1" in result
        assert "This episode was incredible!" in result

        mock_client.get_episode_comments.assert_called_once_with(
            "1", 1, 1, limit=5, sort="newest", page=None
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

    with patch("server.comments.tools.CommentDetailsClient") as mock_client_class:
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

    with patch("server.comments.tools.CommentDetailsClient") as mock_client_class:
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
            "123", limit=5, page=None
        )


@pytest.mark.asyncio
async def test_fetch_movie_comments_error_handling():
    """Test error handling for movie comments."""
    with patch("server.comments.tools.MovieCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_exception(
            TraktResourceNotFoundError("movie", "123", "Movie comments not found.")
        )
        mock_client.get_movie_comments.return_value = comments_future

        with pytest.raises(TraktResourceNotFoundError):
            await fetch_movie_comments(movie_id="123")

        mock_client.get_movie_comments.assert_called_once_with(
            "123", limit=10, sort="newest", page=None
        )


@pytest.mark.asyncio
async def test_fetch_show_comments_error_handling():
    """Test error handling for show comments."""
    with patch("server.comments.tools.ShowCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_exception(
            TraktResourceNotFoundError("show", "123", "Show comments not found.")
        )
        mock_client.get_show_comments.return_value = comments_future

        with pytest.raises(TraktResourceNotFoundError):
            await fetch_show_comments(show_id="123")

        mock_client.get_show_comments.assert_called_once_with(
            "123", limit=10, sort="newest", page=None
        )


@pytest.mark.asyncio
async def test_fetch_season_comments_error_handling():
    """Test error handling for season comments."""
    with patch("server.comments.tools.SeasonCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_exception(
            TraktResourceNotFoundError("season", "1-1", "Season comments not found.")
        )
        mock_client.get_season_comments.return_value = comments_future

        with pytest.raises(TraktResourceNotFoundError):
            await fetch_season_comments(show_id="1", season=1)

        mock_client.get_season_comments.assert_called_once_with(
            "1", 1, limit=10, sort="newest", page=None
        )


@pytest.mark.asyncio
async def test_fetch_episode_comments_error_handling():
    """Test error handling for episode comments."""
    with patch("server.comments.tools.EpisodeCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_exception(
            TraktResourceNotFoundError(
                "episode", "1-1-1", "Episode comments not found."
            )
        )
        mock_client.get_episode_comments.return_value = comments_future

        with pytest.raises(TraktResourceNotFoundError):
            await fetch_episode_comments(show_id="1", season=1, episode=1)

        mock_client.get_episode_comments.assert_called_once_with(
            "1", 1, 1, limit=10, sort="newest", page=None
        )


@pytest.mark.asyncio
async def test_fetch_comment_string_error_handling():
    """Test fetching a comment with a string error response."""
    with patch("server.comments.tools.CommentDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("Error: The requested comment was not found.")
        mock_client.get_comment.return_value = future

        with pytest.raises(Exception) as exc_info:
            await fetch_comment(comment_id="123")

        # Should be an InternalError from handle_api_string_error
        assert "Error accessing comment" in str(exc_info.value)
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

    with patch("server.comments.tools.CommentDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comment_future: asyncio.Future[Any] = asyncio.Future()
        comment_future.set_result(sample_comment)
        mock_client.get_comment.return_value = comment_future

        replies_future: asyncio.Future[Any] = asyncio.Future()
        replies_future.set_result("Error: Unable to fetch replies.")
        mock_client.get_comment_replies.return_value = replies_future

        with pytest.raises(Exception) as exc_info:
            await fetch_comment_replies(comment_id="123", limit=5)

        # Should be an InternalError from handle_api_string_error
        assert "Error accessing comment_replies" in str(exc_info.value)
        mock_client.get_comment.assert_called_once_with("123")
        mock_client.get_comment_replies.assert_called_once_with(
            "123", limit=5, page=None
        )


@pytest.mark.asyncio
async def test_fetch_comment_with_exception():
    """Test comment fetching with exception handling."""
    with patch("server.comments.tools.CommentDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_comment.side_effect = Exception("Network error")

        with pytest.raises(Exception) as exc_info:
            await fetch_comment(comment_id="123")

        # Should be an InternalError from handle_unexpected_error
        assert "An unexpected error occurred" in str(exc_info.value)
        mock_client.get_comment.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_fetch_comment_replies_with_exception():
    """Test comment replies fetching with exception handling."""
    with patch("server.comments.tools.CommentDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_comment.side_effect = Exception("Network error")

        with pytest.raises(Exception) as exc_info:
            await fetch_comment_replies(comment_id="123")

        # Should be an InternalError from handle_unexpected_error
        assert "An unexpected error occurred" in str(exc_info.value)
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

    with patch("server.comments.tools.MovieCommentsClient") as mock_client_class:
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
            "1", limit=10, sort="newest", page=None
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

    with patch("server.comments.tools.ShowCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_show_comments.return_value = comments_future

        result = await fetch_show_comments(show_id="1", sort="likes")

        assert "Show ID: 1" in result
        assert "user1" in result
        assert "This show was amazing!" in result

        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=10, sort="likes", page=None
        )
