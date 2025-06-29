import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.comments.tools import (
    fetch_episode_comments,
    fetch_season_comments,
    fetch_show_comments,
)
from server.shows.tools import (
    fetch_favorited_shows,
    fetch_played_shows,
    fetch_popular_shows,
    fetch_show_ratings,
    fetch_trending_shows,
    fetch_watched_shows,
)


@pytest.mark.asyncio
async def test_fetch_trending_shows():
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

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_trending_shows.return_value = future

        result = await fetch_trending_shows(limit=5)

        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result

        mock_client.get_trending_shows.assert_called_once_with(limit=5)


@pytest.mark.asyncio
async def test_fetch_popular_shows():
    sample_shows = [
        {
            "title": "Breaking Bad",
            "year": 2008,
            "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
        }
    ]

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_popular_shows.return_value = future

        result = await fetch_popular_shows(limit=5)

        assert "# Popular Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        mock_client.get_popular_shows.assert_called_once_with(limit=5)


@pytest.mark.asyncio
async def test_fetch_favorited_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_favorited_shows.return_value = future

        result = await fetch_favorited_shows(limit=5, period="weekly")

        assert "# Most Favorited Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        mock_client.get_favorited_shows.assert_called_once_with(
            limit=5, period="weekly"
        )


@pytest.mark.asyncio
async def test_fetch_played_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_played_shows.return_value = future

        result = await fetch_played_shows(limit=5, period="weekly")

        assert "# Most Played Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        mock_client.get_played_shows.assert_called_once_with(limit=5, period="weekly")


@pytest.mark.asyncio
async def test_fetch_watched_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_watched_shows.return_value = future

        result = await fetch_watched_shows(limit=5, period="weekly")

        assert "# Most Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        mock_client.get_watched_shows.assert_called_once_with(limit=5, period="weekly")


@pytest.mark.asyncio
async def test_fetch_show_comments():
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This is a great show!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123",
        }
    ]

    with (
        patch("server.comments.tools.CommentsClient") as mock_comments_client_class,
    ):
        mock_client = mock_comments_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_show_comments.return_value = comments_future

        result = await fetch_show_comments(show_id="1", limit=5)

        assert "# Comments for Show ID: 1" in result
        assert "user1" in result
        assert "This is a great show!" in result

        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_show_ratings():
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

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        show_future: asyncio.Future[Any] = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_show_ratings.return_value = ratings_future

        result = await fetch_show_ratings(show_id="1")

        assert "# Ratings for Breaking Bad" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 1000 votes" in result

        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_fetch_show_ratings_error():
    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_show.return_value = future

        result = await fetch_show_ratings(show_id="1")

        assert "Error fetching ratings for show ID 1" in result

        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_show_comments_string_error_handling():
    """Test fetching show comments with a string error response."""
    with (
        patch("server.comments.tools.CommentsClient") as mock_comments_client_class,
    ):
        # Configure the mock to return a string error
        mock_client = mock_comments_client_class.return_value

        # Create a future that returns a string error
        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result("Error: The requested show was not found.")
        mock_client.get_show_comments.return_value = comments_future

        # Call the tool function
        result = await fetch_show_comments(show_id="1", limit=5)

        # Verify the result contains the error message
        assert (
            "Error fetching comments for Show ID: 1: Error: The requested show was not found."
            in result
        )

        # Verify the client methods were called
        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_season_comments_string_error_handling():
    """Test fetching season comments with a string error response."""
    with (
        patch("server.comments.tools.CommentsClient") as mock_comments_client_class,
    ):
        # Configure the mock to return a string error
        mock_client = mock_comments_client_class.return_value

        # Create a future that returns a string error
        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result("Error: The requested show was not found.")
        mock_client.get_season_comments.return_value = comments_future

        # Call the tool function
        result = await fetch_season_comments(show_id="1", season=1, limit=5)

        # Verify the result contains the error message
        assert (
            "Error fetching comments for Show ID: 1 - Season 1: Error: The requested show was not found."
            in result
        )

        # Verify the client methods were called
        mock_client.get_season_comments.assert_called_once_with(
            "1", 1, limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_episode_comments_string_error_handling():
    """Test fetching episode comments with a string error response."""
    with (
        patch("server.comments.tools.CommentsClient") as mock_comments_client_class,
    ):
        # Configure the mock to return a string error
        mock_client = mock_comments_client_class.return_value

        # Create a future that returns a string error
        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result("Error: The requested show was not found.")
        mock_client.get_episode_comments.return_value = comments_future

        # Call the tool function
        result = await fetch_episode_comments(show_id="1", season=1, episode=1, limit=5)

        # Verify the result contains the error message
        assert (
            "Error fetching comments for Show ID: 1 - S01E01: Error: The requested show was not found."
            in result
        )

        # Verify the client methods were called
        mock_client.get_episode_comments.assert_called_once_with(
            "1", 1, 1, limit=5, sort="newest"
        )
