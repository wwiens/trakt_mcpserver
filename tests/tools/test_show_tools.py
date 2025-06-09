import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    checkin_to_show,
    fetch_episode_comments,
    fetch_season_comments,
    fetch_show_comments,
    fetch_show_ratings,
    fetch_trending_shows,
    fetch_user_watched_shows,
    search_shows,
)


@pytest.mark.asyncio
async def test_fetch_user_watched_shows_authenticated():
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

    with patch("server.TraktClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future = asyncio.Future()
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
    with (
        patch("server.TraktClient") as mock_client_class,
        patch("server.start_device_auth") as mock_start_auth,
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
async def test_search_shows():
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

    with patch("server.TraktClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_shows.return_value = future

        result = await search_shows(query="breaking bad")

        assert "# Show Search Results" in result
        assert "Breaking Bad (2008)" in result
        assert "ID: 1" in result

        mock_client.search_shows.assert_called_once()
        args, _ = mock_client.search_shows.call_args
        assert args[0] == "breaking bad"  # First positional arg should be the query
        assert args[1] == 10  # Second positional arg should be the limit


@pytest.mark.asyncio
async def test_checkin_to_show_authenticated():
    sample_response = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "show": {"title": "Breaking Bad", "year": 2008},
        "episode": {"season": 1, "number": 1, "title": "Pilot"},
    }

    with patch("server.TraktClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        future = asyncio.Future()
        future.set_result(sample_response)
        mock_client.checkin_to_show.return_value = future

        result = await checkin_to_show(season=1, episode=1, show_id="1")

        assert "# Successfully Checked In" in result
        assert "Breaking Bad" in result
        assert "S01E01" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.checkin_to_show.assert_called_once_with(
            episode_season=1,
            episode_number=1,
            show_id="1",
            show_title=None,
            show_year=None,
            message="",
            share_twitter=False,
            share_mastodon=False,
            share_tumblr=False,
        )


@pytest.mark.asyncio
async def test_checkin_to_show_not_authenticated():
    with (
        patch("server.TraktClient") as mock_client_class,
        patch("server.start_device_auth") as mock_start_auth,
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        mock_start_auth.return_value = (
            "# Trakt Authentication Required\n\nPlease authenticate..."
        )

        result = await checkin_to_show(season=1, episode=1, show_id="1")

        assert "Authentication required" in result
        assert "# Trakt Authentication Required" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.checkin_to_show.assert_not_called()
        mock_start_auth.assert_called_once()


@pytest.mark.asyncio
async def test_checkin_to_show_missing_info():
    with patch("server.TraktClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        result = await checkin_to_show(season=1, episode=1)

        assert "Error: You must provide either a show_id or a show_title" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.checkin_to_show.assert_not_called()


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

    with patch("server.TraktClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_trending_shows.return_value = future

        result = await fetch_trending_shows(limit=5)

        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result

        mock_client.get_trending_shows.assert_called_once_with(limit=5)


@pytest.mark.asyncio
async def test_fetch_show_comments():
    sample_show = {"title": "Breaking Bad", "year": 2008}

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

    with patch("server.TraktClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        show_future = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future

        comments_future = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_show_comments.return_value = comments_future

        result = await fetch_show_comments(show_id="1", limit=5)

        assert "# Comments for Show: Breaking Bad" in result
        assert "user1" in result
        assert "This is a great show!" in result

        mock_client.get_show.assert_called_once_with("1")
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

    with patch("server.TraktClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        show_future = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future

        ratings_future = asyncio.Future()
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
    with patch("server.TraktClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_show.return_value = future

        result = await fetch_show_ratings(show_id="1")

        assert "Error fetching ratings for show ID 1" in result

        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_show_comments_string_error_handling():
    """Test fetching show comments with a string error response."""
    with patch("server.TraktClient") as mock_client_class:
        # Configure the mock to return a string error
        mock_client = mock_client_class.return_value

        # Create a future that returns a string error
        show_future = asyncio.Future()
        show_future.set_result("Error: The requested show was not found.")
        mock_client.get_show.return_value = show_future

        # Call the tool function
        result = await fetch_show_comments(show_id="1", limit=5)

        # Verify the result contains the error message
        assert (
            "Error fetching comments for Show ID: 1: Error: The requested show was not found."
            in result
        )

        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_comments.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_season_comments_string_error_handling():
    """Test fetching season comments with a string error response."""
    with patch("server.TraktClient") as mock_client_class:
        # Configure the mock to return a string error
        mock_client = mock_client_class.return_value

        # Create a future that returns a string error
        show_future = asyncio.Future()
        show_future.set_result("Error: The requested show was not found.")
        mock_client.get_show.return_value = show_future

        # Call the tool function
        result = await fetch_season_comments(show_id="1", season=1, limit=5)

        # Verify the result contains the error message
        assert (
            "Error fetching comments for Show ID: 1 - Season 1: Error: The requested show was not found."
            in result
        )

        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_season_comments.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_episode_comments_string_error_handling():
    """Test fetching episode comments with a string error response."""
    with patch("server.TraktClient") as mock_client_class:
        # Configure the mock to return a string error
        mock_client = mock_client_class.return_value

        # Create a future that returns a string error
        show_future = asyncio.Future()
        show_future.set_result("Error: The requested show was not found.")
        mock_client.get_show.return_value = show_future

        # Call the tool function
        result = await fetch_episode_comments(show_id="1", season=1, episode=1, limit=5)

        # Verify the result contains the error message
        assert (
            "Error fetching comments for Show ID: 1 - S01E01: Error: The requested show was not found."
            in result
        )

        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_episode_comments.assert_not_called()
