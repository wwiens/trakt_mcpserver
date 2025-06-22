import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.user.tools import fetch_user_watched_movies, fetch_user_watched_shows


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
async def test_fetch_user_watched_shows_not_authenticated():
    """Test fetching user watched shows when not authenticated."""
    with (
        patch("server.user.tools.UserClient") as mock_client_class,
        patch("server.user.tools.start_device_auth") as mock_start_auth,
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        mock_start_auth.return_value = (
            "# Trakt Authentication Required\n\nPlease authenticate..."
        )

        result = await fetch_user_watched_shows()

        assert "Authentication required" in result
        assert "# Trakt Authentication Required" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_not_called()
        mock_start_auth.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_watched_shows_with_limit():
    """Test fetching user watched shows with a limit."""
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
        {
            "show": {
                "title": "Stranger Things",
                "year": 2016,
                "overview": "When a young boy disappears, his mother, a police chief and his friends must confront terrifying supernatural forces.",
            },
            "last_watched_at": "2023-01-05T22:15:00Z",
            "plays": 8,
        },
    ]

    with patch("server.user.tools.UserClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_user_watched_shows.return_value = future

        result = await fetch_user_watched_shows(limit=2)

        # Should contain first 2 shows
        assert "Breaking Bad (2008)" in result
        assert "The Office (2005)" in result
        # Should not contain third show
        assert "Stranger Things (2016)" not in result

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
async def test_fetch_user_watched_movies_not_authenticated():
    """Test fetching user watched movies when not authenticated."""
    with (
        patch("server.user.tools.UserClient") as mock_client_class,
        patch("server.user.tools.start_device_auth") as mock_start_auth,
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        mock_start_auth.return_value = (
            "# Trakt Authentication Required\n\nPlease authenticate..."
        )

        result = await fetch_user_watched_movies()

        assert "Authentication required" in result
        assert "# Trakt Authentication Required" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_not_called()
        mock_start_auth.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_watched_movies_with_limit():
    """Test fetching user watched movies with a limit."""
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
        {
            "movie": {
                "title": "Interstellar",
                "year": 2014,
                "overview": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            },
            "last_watched_at": "2023-02-05T21:30:00Z",
            "plays": 1,
        },
    ]

    with patch("server.user.tools.UserClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_user_watched_movies.return_value = future

        result = await fetch_user_watched_movies(limit=2)

        # Should contain first 2 movies
        assert "Inception (2010)" in result
        assert "The Matrix (1999)" in result
        # Should not contain third movie
        assert "Interstellar (2014)" not in result

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
