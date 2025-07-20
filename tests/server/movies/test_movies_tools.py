import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.comments.tools import fetch_movie_comments
from server.movies.tools import (
    fetch_movie_ratings,
    fetch_movie_summary,
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
async def test_fetch_movie_ratings_error():
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie.return_value = future

        result = await fetch_movie_ratings(movie_id="1")

        assert "Error fetching ratings for movie ID 1" in result

        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_movie_comments_string_error_handling():
    """Test fetching movie comments with a string error response."""
    with patch("server.comments.tools.CommentsClient") as mock_client_class:
        # Configure the mock to return a string error
        mock_client = mock_client_class.return_value

        # Create a future that returns a string error
        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result("Error: The requested movie was not found.")
        mock_client.get_movie_comments.return_value = comments_future

        # Call the tool function
        result = await fetch_movie_comments(movie_id="1", limit=5)

        # Verify the result contains the error message
        assert (
            "Error fetching comments for Movie ID: 1: Error: The requested movie was not found."
            in result
        )

        # Verify the client methods were called
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
        "overview": "A computer hacker learns about the true nature of reality.",
        "ids": {"trakt": 12345},
    }

    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        movie_future: asyncio.Future[Any] = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future

        result = await fetch_movie_summary(movie_id="12345", extended=False)

        assert "## The Matrix (1999)" in result
        assert "A computer hacker learns about the true nature of reality." in result
        assert "Trakt ID: 12345" in result
        # Should not contain extended data
        assert "- Status:" not in result
        assert "- Runtime:" not in result
        assert "- Certification:" not in result

        mock_client.get_movie.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_extended_error():
    """Test fetching movie summary with extended mode error."""
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie_extended.return_value = future

        result = await fetch_movie_summary(movie_id="12345")

        assert "Error fetching movie summary for ID 12345" in result
        mock_client.get_movie_extended.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_basic_error():
    """Test fetching movie summary with basic mode error."""
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie.return_value = future

        result = await fetch_movie_summary(movie_id="12345", extended=False)

        assert "Error fetching movie summary for ID 12345" in result
        mock_client.get_movie.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_extended_string_error():
    """Test fetching movie summary with extended mode string error response."""
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("Error: Movie not found")
        mock_client.get_movie_extended.return_value = future

        result = await fetch_movie_summary(movie_id="12345")

        assert (
            "Error fetching movie summary for ID 12345: Error: Movie not found"
            in result
        )
        mock_client.get_movie_extended.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_basic_string_error():
    """Test fetching movie summary with basic mode string error response."""
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("Error: Movie not found")
        mock_client.get_movie.return_value = future

        result = await fetch_movie_summary(movie_id="12345", extended=False)

        assert (
            "Error fetching movie summary for ID 12345: Error: Movie not found"
            in result
        )
        mock_client.get_movie.assert_called_once_with("12345")
