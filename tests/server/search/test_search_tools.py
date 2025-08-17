"""Tests for search tools."""

import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.search.tools import search_movies, search_shows
from utils.api.errors import InternalError


@pytest.mark.asyncio
async def test_search_shows():
    """Test searching for shows."""
    sample_results = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
                "ids": {"trakt": "1"},
            }
        }
    ]

    with patch("server.search.tools.SearchClient") as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value

        # Create awaitable result
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_shows.return_value = future

        # Call the tool function
        result = await search_shows(query="breaking bad")

        # Verify the result
        assert "# Show Search Results" in result
        assert "Breaking Bad (2008)" in result
        assert "ID: 1" in result

        # Verify the client methods were called
        mock_client.search_shows.assert_called_once()
        args, _ = mock_client.search_shows.call_args
        assert args[0] == "breaking bad"  # First positional arg should be the query
        assert args[1] == 10  # Second positional arg should be the limit (default)


@pytest.mark.asyncio
async def test_search_shows_with_limit():
    """Test searching for shows with custom limit."""
    sample_results = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
                "ids": {"trakt": "1"},
            }
        }
    ]

    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_shows.return_value = future

        result = await search_shows(query="breaking bad", limit=5)

        assert "# Show Search Results" in result
        assert "Breaking Bad (2008)" in result

        mock_client.search_shows.assert_called_once()
        args, _ = mock_client.search_shows.call_args
        assert args[0] == "breaking bad"
        assert args[1] == 5  # Custom limit


@pytest.mark.asyncio
async def test_search_shows_empty_results():
    """Test searching for shows with no results."""
    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result([])  # Empty results
        mock_client.search_shows.return_value = future

        result = await search_shows(query="nonexistent show")

        assert "# Show Search Results" in result
        mock_client.search_shows.assert_called_once()


@pytest.mark.asyncio
async def test_search_shows_error_handling():
    """Test searching for shows with API error."""
    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.search_shows.return_value = future

        with pytest.raises(InternalError) as exc_info:
            await search_shows(query="breaking bad")

        # The function should raise an InternalError for unexpected exceptions
        assert exc_info.value.code == -32603  # INTERNAL_ERROR code
        assert (
            "An unexpected error occurred during search shows" in exc_info.value.message
        )

        # Optionally check structured data
        if exc_info.value.data:
            assert exc_info.value.data.get("operation") == "search shows"
            assert exc_info.value.data.get("error_type") == "unexpected_error"


@pytest.mark.asyncio
async def test_search_movies():
    """Test searching for movies."""
    sample_results = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
                "ids": {"trakt": "1"},
            }
        }
    ]

    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_movies.return_value = future

        result = await search_movies(query="inception")

        assert "# Movie Search Results" in result
        assert "Inception (2010)" in result
        assert "ID: 1" in result

        mock_client.search_movies.assert_called_once()
        args, _ = mock_client.search_movies.call_args
        assert args[0] == "inception"  # First positional arg should be the query
        assert args[1] == 10  # Second positional arg should be the limit (default)


@pytest.mark.asyncio
async def test_search_movies_with_limit():
    """Test searching for movies with custom limit."""
    sample_results = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
                "ids": {"trakt": "1"},
            }
        }
    ]

    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_movies.return_value = future

        result = await search_movies(query="inception", limit=3)

        assert "# Movie Search Results" in result
        assert "Inception (2010)" in result

        mock_client.search_movies.assert_called_once()
        args, _ = mock_client.search_movies.call_args
        assert args[0] == "inception"
        assert args[1] == 3  # Custom limit


@pytest.mark.asyncio
async def test_search_movies_empty_results():
    """Test searching for movies with no results."""
    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result([])  # Empty results
        mock_client.search_movies.return_value = future

        result = await search_movies(query="nonexistent movie")

        assert "# Movie Search Results" in result
        mock_client.search_movies.assert_called_once()


@pytest.mark.asyncio
async def test_search_movies_error_handling():
    """Test searching for movies with API error."""
    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.search_movies.return_value = future

        with pytest.raises(InternalError) as exc_info:
            await search_movies(query="inception")

        # The function should raise an InternalError for unexpected exceptions
        assert exc_info.value.code == -32603  # INTERNAL_ERROR code
        assert (
            "An unexpected error occurred during search movies"
            in exc_info.value.message
        )

        # Optionally check structured data
        if exc_info.value.data:
            assert exc_info.value.data.get("operation") == "search movies"
            assert exc_info.value.data.get("error_type") == "unexpected_error"


@pytest.mark.asyncio
async def test_search_shows_multiple_results():
    """Test searching for shows with multiple results."""
    sample_results = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
                "ids": {"trakt": "1"},
            }
        },
        {
            "show": {
                "title": "Better Call Saul",
                "year": 2015,
                "overview": "The trials and tribulations of criminal lawyer Jimmy McGill.",
                "ids": {"trakt": "2"},
            }
        },
    ]

    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_shows.return_value = future

        result = await search_shows(query="breaking")

        assert "# Show Search Results" in result
        assert "Breaking Bad (2008)" in result
        assert "Better Call Saul (2015)" in result
        assert "ID: 1" in result
        assert "ID: 2" in result


@pytest.mark.asyncio
async def test_search_movies_multiple_results():
    """Test searching for movies with multiple results."""
    sample_results = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
                "ids": {"trakt": "1"},
            }
        },
        {
            "movie": {
                "title": "Interstellar",
                "year": 2014,
                "overview": "A team of explorers travel through a wormhole in space.",
                "ids": {"trakt": "2"},
            }
        },
    ]

    with patch("server.search.tools.SearchClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_movies.return_value = future

        result = await search_movies(query="in")

        assert "# Movie Search Results" in result
        assert "Inception (2010)" in result
        assert "Interstellar (2014)" in result
        assert "ID: 1" in result
        assert "ID: 2" in result
