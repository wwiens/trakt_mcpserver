import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from config.errors import AUTH_REQUIRED
from utils.api.errors import InternalError, InvalidRequestError

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.comments.tools import fetch_movie_comments
from server.movies.tools import (
    fetch_movie_ratings,
    fetch_movie_summary,
    fetch_popular_movies,
    fetch_trending_movies,
)


@pytest.mark.asyncio
async def test_fetch_trending_movies():
    sample_movies = [
        {
            "watchers": 150,
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
            },
        }
    ]

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_trending_movies.return_value = future

        result = await fetch_trending_movies(limit=5)

        assert "# Trending Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "150 watchers" in result

        mock_client.get_trending_movies.assert_called_once_with(limit=5)


@pytest.mark.asyncio
async def test_fetch_movie_comments():
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This is a great movie!",
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
        mock_client.get_movie_comments.return_value = comments_future

        result = await fetch_movie_comments(movie_id="1", limit=5)

        assert "# Comments for Movie ID: 1" in result
        assert "user1" in result
        assert "This is a great movie!" in result

        mock_client.get_movie_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_movie_ratings():
    sample_movie = {"title": "Inception", "year": 2010}

    sample_ratings = {
        "rating": 9.0,
        "votes": 2000,
        "distribution": {
            "10": 800,
            "9": 600,
            "8": 300,
            "7": 150,
            "6": 80,
            "5": 40,
            "4": 20,
            "3": 5,
            "2": 3,
            "1": 2,
        },
    }

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        movie_future: asyncio.Future[Any] = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_movie_ratings.return_value = ratings_future

        result = await fetch_movie_ratings(movie_id="1")

        assert "# Ratings for Inception" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 2000 votes" in result

        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_fetch_movie_ratings_error_propagation():
    """Test that exceptions from client methods propagate through server tools."""
    from utils.api.errors import InvalidRequestError

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client to raise MCP error
        mock_client.get_movie.side_effect = InvalidRequestError(
            AUTH_REQUIRED,
            data={"http_status": 401},
        )

        # The server tool should let the exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_movie_ratings(movie_id="1")

        assert "Authentication required" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 401

        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_movie_comments_error_propagation():
    """Test that movie comments fetch errors propagate correctly."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client method to raise InvalidRequestError
        async def async_raise_error(*args: Any, **kwargs: Any) -> None:
            raise InvalidRequestError("The requested movie was not found.", -32600)

        mock_client.get_movie_comments.side_effect = async_raise_error

        # Server tool should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_movie_comments(movie_id="1", limit=5)

        assert exc_info.value.code == -32600
        assert "The requested movie was not found." in str(exc_info.value)
        mock_client.get_movie_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_movie_summary_extended():
    """Test fetching movie summary with extended data (default)."""
    sample_movie = {
        "title": "The Matrix",
        "year": 1999,
        "ids": {"trakt": 12345},
        "tagline": "The future is not set.",
        "overview": "A computer hacker learns about the true nature of reality.",
        "released": "1999-03-31",
        "runtime": 136,
        "country": "us",
        "status": "released",
        "rating": 8.7,
        "votes": 150,
        "comment_count": 75,
        "languages": ["en"],
        "genres": ["action", "sci-fi"],
        "certification": "R",
        "homepage": "http://www.thematrix.com/",
    }

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        movie_future: asyncio.Future[Any] = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie_extended.return_value = movie_future

        result = await fetch_movie_summary(movie_id="12345")

        assert "## The Matrix (1999) - Released" in result
        assert "*The future is not set.*" in result
        assert "A computer hacker learns about the true nature of reality." in result
        assert "- Status: released" in result
        assert "- Runtime: 136 minutes" in result
        assert "- Certification: R" in result
        assert "- Released: 1999-03-31" in result
        assert "- Country: US" in result
        assert "- Genres: action, sci-fi" in result
        assert "- Languages: en" in result
        assert "- Homepage: http://www.thematrix.com/" in result
        assert "- Rating: 8.7/10 (150 votes)" in result
        assert "- Comments: 75" in result
        assert "Trakt ID: 12345" in result

        mock_client.get_movie_extended.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_basic():
    """Test fetching movie summary with basic data only."""
    sample_movie = {
        "title": "The Matrix",
        "year": 1999,
        "ids": {"trakt": 12345},
    }

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        movie_future: asyncio.Future[Any] = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future

        result = await fetch_movie_summary(movie_id="12345", extended=False)

        assert "## The Matrix (1999)" in result
        assert "Trakt ID: 12345" in result
        # Should not contain extended data
        assert "- Status:" not in result
        assert "- Runtime:" not in result
        assert "- Certification:" not in result

        mock_client.get_movie.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_extended_error_propagation():
    """Test that exceptions from client methods propagate through server tools."""
    from utils.api.errors import InvalidRequestError

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client to raise MCP error
        mock_client.get_movie_extended.side_effect = InvalidRequestError(
            "The requested resource was not found.", data={"http_status": 404}
        )

        # The server tool should let the exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_movie_summary(movie_id="12345")

        assert "not found" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 404

        mock_client.get_movie_extended.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_basic_error_propagation():
    """Test that exceptions from client methods propagate through server tools."""
    from utils.api.errors import InternalError

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client to raise MCP error
        mock_client.get_movie.side_effect = InternalError(
            "HTTP 500 error occurred",
            data={"http_status": 500, "response": "Internal Server Error"},
        )

        # The server tool should let the exception propagate
        with pytest.raises(InternalError) as exc_info:
            await fetch_movie_summary(movie_id="12345", extended=False)

        assert "HTTP 500 error occurred" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 500

        mock_client.get_movie.assert_called_once_with("12345")


# New comprehensive error handling tests for Phase 3


@pytest.mark.asyncio
async def test_fetch_movie_ratings_second_api_call_error_propagation():
    """Test error propagation from the second API call (get_movie_ratings)."""
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # First call succeeds
        async def async_return_movie():
            return {"title": "Test Movie", "year": 2023}

        mock_client.get_movie.return_value = async_return_movie()

        # Second call raises exception
        async def async_raise_error(*args: Any, **kwargs: Any) -> None:
            raise InvalidRequestError("Ratings not available", -32600)

        mock_client.get_movie_ratings.side_effect = async_raise_error

        # Server tool should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_movie_ratings(movie_id="123")

        assert exc_info.value.code == -32600
        assert "Ratings not available" in str(exc_info.value)
        mock_client.get_movie.assert_called_once_with("123")
        mock_client.get_movie_ratings.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_fetch_movie_ratings_multiple_error_types():
    """Test different MCP error types propagate correctly."""
    test_cases = [
        (
            InvalidRequestError(
                "Rate limit exceeded. Please try again later.",
                data={"http_status": 429},
            ),
            429,
        ),
        (
            InvalidRequestError(
                "Access forbidden. You don't have permission.",
                data={"http_status": 403},
            ),
            403,
        ),
        (
            InternalError(
                "Unable to connect to Trakt API.", data={"error_type": "request_error"}
            ),
            None,
        ),
    ]

    for error, expected_status in test_cases:
        with patch("server.movies.tools.MoviesClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_movie.side_effect = error

            with pytest.raises(type(error)) as exc_info:
                await fetch_movie_ratings(movie_id="123")

            assert exc_info.value.message == error.message
            if expected_status:
                assert exc_info.value.data is not None
                assert exc_info.value.data["http_status"] == expected_status


@pytest.mark.asyncio
async def test_fetch_trending_movies_error_propagation():
    """Test that trending movies tool propagates MCP errors correctly."""
    from utils.api.errors import InvalidRequestError

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_client.get_trending_movies.side_effect = InvalidRequestError(
            AUTH_REQUIRED,
            data={"http_status": 401},
        )

        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_trending_movies(limit=10)

        assert "Authentication required" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 401
        mock_client.get_trending_movies.assert_called_once_with(limit=10)


@pytest.mark.asyncio
async def test_fetch_popular_movies_error_propagation():
    """Test that popular movies tool propagates MCP errors correctly."""
    from utils.api.errors import InternalError

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_client.get_popular_movies.side_effect = InternalError(
            "HTTP 500 error occurred",
            data={"http_status": 500, "response": "Internal Server Error"},
        )

        with pytest.raises(InternalError) as exc_info:
            await fetch_popular_movies(limit=5)

        assert "HTTP 500 error occurred" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 500
        mock_client.get_popular_movies.assert_called_once_with(limit=5)
