import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.user.resources import get_user_watched_movies, get_user_watched_shows


@pytest.mark.asyncio
async def test_get_user_watched_shows_authenticated():
    """Test getting user watched shows when authenticated."""
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            },
            "last_watched_at": "2023-01-15T20:30:00Z",
            "plays": 5,
        }
    ]

    with patch("server.user.resources.UserClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_user_watched_shows.return_value = future

        # Call the resource function
        result = await get_user_watched_shows()

        # Verify the result
        assert "# Your Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "Plays: 5" in result

        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_watched_shows_not_authenticated():
    """Test getting user watched shows when not authenticated."""
    with patch("server.user.resources.UserClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        # Call the resource function
        result = await get_user_watched_shows()

        # Verify the result
        assert "# Authentication Required" in result
        assert "You need to authenticate with Trakt" in result

        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_watched_movies_authenticated():
    """Test getting user watched movies when authenticated."""
    sample_movies = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
            },
            "last_watched_at": "2023-02-15T20:30:00Z",
            "plays": 3,
        }
    ]

    with patch("server.user.resources.UserClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_user_watched_movies.return_value = future

        # Call the resource function
        result = await get_user_watched_movies()

        # Verify the result
        assert "# Your Watched Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "Plays: 3" in result

        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_watched_movies_not_authenticated():
    """Test getting user watched movies when not authenticated."""
    with patch("server.user.resources.UserClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        # Call the resource function
        result = await get_user_watched_movies()

        # Verify the result
        assert "# Authentication Required" in result
        assert "You need to authenticate with Trakt" in result

        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_not_called()
