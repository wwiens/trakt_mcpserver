import asyncio
import sys
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import pytest

from utils.api.error_types import AuthenticationRequiredError

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.user.tools import fetch_user_watched_movies, fetch_user_watched_shows
from tests.types_stub import MCPErrorWithData  # noqa: TC001


@pytest.mark.asyncio
async def test_fetch_user_watched_shows_authenticated():
    """Test fetching user watched shows when authenticated."""
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

    with patch("server.user.tools.UserClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_user_watched_shows.return_value = future

        result = await fetch_user_watched_shows()

        assert "# Your Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "Plays: 5" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_watched_movies_authenticated():
    """Test fetching user watched movies when authenticated."""
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

    with patch("server.user.tools.UserClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_user_watched_movies.return_value = future

        result = await fetch_user_watched_movies()

        assert "# Your Watched Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "Plays: 3" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_watched_shows_limit_zero():
    """Test fetching user watched shows with limit=0 (no limit)."""
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            },
            "last_watched_at": "2023-01-15T20:30:00Z",
            "plays": 5,
        },
        {
            "show": {
                "title": "The Office",
                "year": 2005,
                "overview": "A mockumentary on a group of typical office workers.",
            },
            "last_watched_at": "2023-01-10T18:00:00Z",
            "plays": 12,
        },
    ]

    with patch("server.user.tools.UserClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_user_watched_shows.return_value = future

        result = await fetch_user_watched_shows(limit=0)

        # Should contain all shows
        assert "Breaking Bad (2008)" in result
        assert "The Office (2005)" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_watched_movies_limit_zero():
    """Test fetching user watched movies with limit=0 (no limit)."""
    sample_movies = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
            },
            "last_watched_at": "2023-02-15T20:30:00Z",
            "plays": 3,
        },
        {
            "movie": {
                "title": "The Matrix",
                "year": 1999,
                "overview": "A computer hacker learns from mysterious rebels about the true nature of reality.",
            },
            "last_watched_at": "2023-02-10T19:45:00Z",
            "plays": 2,
        },
    ]

    with patch("server.user.tools.UserClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_user_watched_movies.return_value = future

        result = await fetch_user_watched_movies(limit=0)

        # Should contain all movies
        assert "Inception (2010)" in result
        assert "The Matrix (1999)" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_watched_shows_not_authenticated():
    """Test fetching user watched shows when not authenticated."""
    with patch("server.user.tools.UserClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        with pytest.raises(AuthenticationRequiredError) as exc_info:
            await fetch_user_watched_shows()

        # Verify error contains expected information
        error = cast("MCPErrorWithData", exc_info.value)
        assert error.data["error_type"] == "auth_required"
        mock_client.is_authenticated.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_watched_movies_not_authenticated():
    """Test fetching user watched movies when not authenticated."""
    with patch("server.user.tools.UserClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        with pytest.raises(AuthenticationRequiredError) as exc_info:
            await fetch_user_watched_movies()

        # Verify error contains expected information
        error = cast("MCPErrorWithData", exc_info.value)
        assert error.data["error_type"] == "auth_required"
        mock_client.is_authenticated.assert_called_once()
