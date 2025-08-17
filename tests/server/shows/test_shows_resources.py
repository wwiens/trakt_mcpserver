import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.shows.resources import (
    get_favorited_shows,
    get_played_shows,
    get_popular_shows,
    get_show_ratings,
    get_trending_shows,
    get_watched_shows,
)
from utils.api.errors import InternalError


@pytest.mark.asyncio
async def test_get_trending_shows():
    sample_shows = [
        {
            "watchers": 100,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            },
        }
    ]

    with patch("server.shows.resources.ShowsClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_trending_shows.return_value = future

        # Call the resource function
        result = await get_trending_shows()

        # Verify the result
        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result

        # Verify the client methods were called
        mock_client.get_trending_shows.assert_called_once()


@pytest.mark.asyncio
async def test_get_popular_shows():
    sample_shows = [
        {
            "title": "Breaking Bad",
            "year": 2008,
            "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
        }
    ]

    with patch("server.shows.resources.ShowsClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_popular_shows.return_value = future

        # Call the resource function
        result = await get_popular_shows()

        # Verify the result
        assert "# Popular Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        # Verify the client methods were called
        mock_client.get_popular_shows.assert_called_once()


@pytest.mark.asyncio
async def test_get_favorited_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.resources.ShowsClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_favorited_shows.return_value = future

        # Call the resource function
        result = await get_favorited_shows()

        # Verify the result
        assert "# Most Favorited Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        # Verify the client methods were called
        mock_client.get_favorited_shows.assert_called_once()


@pytest.mark.asyncio
async def test_get_played_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.resources.ShowsClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_played_shows.return_value = future

        # Call the resource function
        result = await get_played_shows()

        # Verify the result
        assert "# Most Played Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        # Verify the client methods were called
        mock_client.get_played_shows.assert_called_once()


@pytest.mark.asyncio
async def test_get_watched_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.resources.ShowsClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_watched_shows.return_value = future

        # Call the resource function
        result = await get_watched_shows()

        # Verify the result
        assert "# Most Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        # Verify the client methods were called
        mock_client.get_watched_shows.assert_called_once()


@pytest.mark.asyncio
async def test_get_show_ratings():
    sample_show = {"title": "Breaking Bad", "year": 2008}

    sample_ratings = {
        "rating": 9.0,
        "votes": 1000,
        "distribution": {
            "10": 500,
            "9": 300,
            "8": 100,
            "7": 50,
            "6": 20,
            "5": 15,
            "4": 10,
            "3": 3,
            "2": 1,
            "1": 1,
        },
    }

    with patch("server.shows.resources.ShowsClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable results
        show_future: asyncio.Future[Any] = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_show_ratings.return_value = ratings_future

        # Call the resource function
        result = await get_show_ratings("1")

        # Verify the result
        assert "# Ratings for Breaking Bad" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 1000 votes" in result

        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_get_show_ratings_error_handling():
    with patch("server.shows.resources.ShowsClient") as mock_client_class:
        # Configure the mock to raise an exception
        mock_client = mock_client_class.return_value

        # Create a future that raises an exception
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_show.return_value = future

        # Call the resource function - should raise exception
        with pytest.raises(InternalError) as exc_info:
            await get_show_ratings("1")

        # Verify it's an InternalError for unexpected exceptions
        assert "An unexpected error occurred" in str(exc_info.value)

        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_get_show_ratings_string_error_handling():
    with patch("server.shows.resources.ShowsClient") as mock_client_class:
        # Configure the mock to return a string error
        mock_client = mock_client_class.return_value

        # Create a future that returns a string error
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("Error: The requested resource was not found.")
        mock_client.get_show.return_value = future

        # handle_api_string_error returns InternalError for string errors
        with pytest.raises(InternalError) as exc_info:
            await get_show_ratings("1")

        # Check that it's an InternalError
        assert "Error accessing show" in str(
            exc_info.value
        ) or "An unexpected error occurred" in str(exc_info.value)

        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()
