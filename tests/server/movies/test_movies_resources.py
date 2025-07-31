import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from utils.api.errors import InvalidRequestError

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.movies.resources import (
    get_movie_ratings,
    get_popular_movies,
    get_trending_movies,
)


@pytest.mark.asyncio
async def test_get_trending_movies():
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

    with patch("server.movies.resources.MoviesClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_trending_movies.return_value = future

        # Call the resource function
        result = await get_trending_movies()

        # Verify the result
        assert "# Trending Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "150 watchers" in result

        # Verify the client methods were called
        mock_client.get_trending_movies.assert_called_once()


@pytest.mark.asyncio
async def test_get_popular_movies():
    sample_movies = [
        {
            "title": "Inception",
            "year": 2010,
            "overview": "A thief who steals corporate secrets through dream-sharing technology.",
        }
    ]

    with patch("server.movies.resources.MoviesClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_popular_movies.return_value = future

        # Call the resource function
        result = await get_popular_movies()

        # Verify the result
        assert "# Popular Movies on Trakt" in result
        assert "Inception (2010)" in result

        # Verify the client methods were called
        mock_client.get_popular_movies.assert_called_once()


@pytest.mark.asyncio
async def test_get_movie_ratings():
    sample_movie = {"title": "Inception", "year": 2010}

    sample_ratings = {
        "rating": 8.5,
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

    with patch("server.movies.resources.MoviesClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable results
        movie_future: asyncio.Future[Any] = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_movie_ratings.return_value = ratings_future

        # Call the resource function
        result = await get_movie_ratings("1")

        # Verify the result
        assert "# Ratings for Inception" in result
        assert "**Average Rating:** 8.50/10" in result
        assert "from 2000 votes" in result

        # Verify the client methods were called
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_get_movie_ratings_error_handling():
    with patch("server.movies.resources.MoviesClient") as mock_client_class:
        # Configure the mock to raise an exception
        mock_client = mock_client_class.return_value

        # Create a future that raises an exception
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie.return_value = future

        # Call the resource function and expect the exception to propagate
        with pytest.raises(Exception, match="API error"):
            await get_movie_ratings("1")

        # Verify the client methods were called
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_get_movie_ratings_error_propagation():
    """Test that movie ratings resource errors propagate correctly."""
    with patch("server.movies.resources.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client method to raise InvalidRequestError
        async def async_raise_error(*args: Any, **kwargs: Any) -> None:
            raise InvalidRequestError("The requested resource was not found.", -32600)

        mock_client.get_movie.side_effect = async_raise_error

        # Server resource should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await get_movie_ratings("1")

        assert exc_info.value.code == -32600
        assert "The requested resource was not found." in str(exc_info.value)
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_not_called()
