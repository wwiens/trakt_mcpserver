import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from config.errors import AUTH_REQUIRED
from utils.api.errors import InternalError, InvalidRequestError

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
    fetch_show_summary,
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
async def test_fetch_show_ratings_auth_error_propagation():
    """Test that exceptions from client methods propagate through server tools."""
    from utils.api.errors import InvalidRequestError

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client to raise MCP error
        mock_client.get_show.side_effect = InvalidRequestError(
            AUTH_REQUIRED,
            data={"http_status": 401},
        )

        # The server tool should let the exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_show_ratings(show_id="1")

        assert "Authentication required" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 401

        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_show_comments_error_propagation():
    """Test that show comments fetch errors propagate correctly."""
    with (
        patch("server.comments.tools.CommentsClient") as mock_comments_client_class,
    ):
        mock_client = mock_comments_client_class.return_value

        # Mock client method to raise InvalidRequestError
        async def async_raise_error(*args: Any, **kwargs: Any) -> None:
            raise InvalidRequestError("The requested show was not found.", -32600)

        mock_client.get_show_comments.side_effect = async_raise_error

        # Server tool should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_show_comments(show_id="1", limit=5)

        assert exc_info.value.code == -32600
        assert "The requested show was not found." in str(exc_info.value)
        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_season_comments_error_propagation():
    """Test that season comments fetch errors propagate correctly."""
    with (
        patch("server.comments.tools.CommentsClient") as mock_comments_client_class,
    ):
        mock_client = mock_comments_client_class.return_value

        # Mock client method to raise InvalidRequestError
        mock_client.get_season_comments.side_effect = InvalidRequestError(
            "The requested show was not found.", -32600
        )

        # Server tool should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_season_comments(show_id="1", season=1, limit=5)

        assert exc_info.value.code == -32600
        assert "The requested show was not found." in str(exc_info.value)
        mock_client.get_season_comments.assert_called_once_with(
            "1", 1, limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_episode_comments_error_propagation():
    """Test that episode comments fetch errors propagate correctly."""
    with (
        patch("server.comments.tools.CommentsClient") as mock_comments_client_class,
    ):
        mock_client = mock_comments_client_class.return_value

        # Mock client method to raise InvalidRequestError
        mock_client.get_episode_comments.side_effect = InvalidRequestError(
            "The requested show was not found.", -32600
        )

        # Server tool should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_episode_comments(show_id="1", season=1, episode=1, limit=5)

        assert exc_info.value.code == -32600
        assert "The requested show was not found." in str(exc_info.value)
        mock_client.get_episode_comments.assert_called_once_with(
            "1", 1, 1, limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_show_summary_extended():
    """Test fetching show summary with extended data (default)."""
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008,
        "ids": {"trakt": 54321},
        "tagline": "Chemistry is the study of change.",
        "overview": "A high school chemistry teacher turned meth producer.",
        "first_aired": "2008-01-20T02:00:00.000Z",
        "airs": {"day": "Sunday", "time": "21:00", "timezone": "America/New_York"},
        "runtime": 47,
        "certification": "TV-MA",
        "network": "AMC",
        "country": "us",
        "status": "ended",
        "rating": 9.5,
        "votes": 200,
        "comment_count": 150,
        "languages": ["en"],
        "genres": ["drama", "crime"],
        "aired_episodes": 62,
        "homepage": "http://www.amc.com/shows/breaking-bad",
    }

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        show_future: asyncio.Future[Any] = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show_extended.return_value = show_future

        result = await fetch_show_summary(show_id="54321")

        assert "## Breaking Bad (2008) - Ended" in result
        assert "*Chemistry is the study of change.*" in result
        assert "A high school chemistry teacher turned meth producer." in result
        assert "- Status: ended" in result
        assert "- Runtime: 47 minutes" in result
        assert "- Certification: TV-MA" in result
        assert "- Network: AMC" in result
        assert "- Air Time: Sundays at 21:00 (America/New_York)" in result
        assert "- Aired Episodes: 62" in result
        assert "- Country: US" in result
        assert "- Genres: drama, crime" in result
        assert "- Languages: en" in result
        assert "- Homepage: http://www.amc.com/shows/breaking-bad" in result
        assert "- Rating: 9.5/10 (200 votes)" in result
        assert "- Comments: 150" in result
        assert "Trakt ID: 54321" in result

        mock_client.get_show_extended.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_basic():
    """Test fetching show summary with basic data only."""
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008,
        "ids": {"trakt": 54321},
    }

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        show_future: asyncio.Future[Any] = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future

        result = await fetch_show_summary(show_id="54321", extended=False)

        assert "## Breaking Bad (2008)" in result
        assert "Trakt ID: 54321" in result
        # Should not contain extended data
        assert "- Status:" not in result
        assert "- Runtime:" not in result
        assert "- Network:" not in result
        assert "- Air Time:" not in result

        mock_client.get_show.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_extended_invalid_request_error():
    """Test that exceptions from client methods propagate through server tools."""
    from utils.api.errors import InvalidRequestError

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client to raise MCP error
        mock_client.get_show_extended.side_effect = InvalidRequestError(
            "The requested resource was not found.", data={"http_status": 404}
        )

        # The server tool should let the exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_show_summary(show_id="54321")

        assert "not found" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 404

        mock_client.get_show_extended.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_basic_internal_error():
    """Test that exceptions from client methods propagate through server tools."""
    from utils.api.errors import InternalError

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client to raise MCP error
        mock_client.get_show.side_effect = InternalError(
            "HTTP 500 error occurred",
            data={"http_status": 500, "response": "Internal Server Error"},
        )

        # The server tool should let the exception propagate
        with pytest.raises(InternalError) as exc_info:
            await fetch_show_summary(show_id="54321", extended=False)

        assert "HTTP 500 error occurred" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 500

        mock_client.get_show.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_extended_error_propagation():
    """Test that show summary extended fetch errors propagate correctly."""
    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client method to raise InvalidRequestError
        mock_client.get_show_extended.side_effect = InvalidRequestError(
            "Show not found", -32600
        )

        # Server tool should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_show_summary(show_id="54321")

        assert exc_info.value.code == -32600
        assert "Show not found" in str(exc_info.value)
        mock_client.get_show_extended.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_basic_error_propagation():
    """Test that show summary basic fetch errors propagate correctly."""
    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client method to raise InvalidRequestError
        mock_client.get_show.side_effect = InvalidRequestError("Show not found", -32600)

        # Server tool should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_show_summary(show_id="54321", extended=False)

        assert exc_info.value.code == -32600
        assert "Show not found" in str(exc_info.value)
        mock_client.get_show.assert_called_once_with("54321")


# New comprehensive error handling tests for Phase 3


@pytest.mark.asyncio
async def test_fetch_show_ratings_error_propagation():
    """Test that show ratings fetch errors propagate correctly."""
    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock client method to raise InvalidRequestError
        mock_client.get_show.side_effect = InvalidRequestError("Show not found", -32600)

        # Server tool should let the MCP exception propagate
        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_show_ratings(show_id="invalid_id")

        assert exc_info.value.code == -32600
        assert "Show not found" in str(exc_info.value)
        mock_client.get_show.assert_called_once_with("invalid_id")
        mock_client.get_show_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_show_ratings_multiple_error_types():
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
        with patch("server.shows.tools.ShowsClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_show.side_effect = error

            with pytest.raises(type(error)) as exc_info:
                await fetch_show_ratings(show_id="123")

            assert exc_info.value.message == error.message
            if expected_status:
                assert exc_info.value.data is not None
                assert exc_info.value.data["http_status"] == expected_status


@pytest.mark.asyncio
async def test_fetch_trending_shows_error_propagation():
    """Test that trending shows tool propagates MCP errors correctly."""
    from utils.api.errors import InvalidRequestError

    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_client.get_trending_shows.side_effect = InvalidRequestError(
            AUTH_REQUIRED,
            data={"http_status": 401},
        )

        with pytest.raises(InvalidRequestError) as exc_info:
            await fetch_trending_shows(limit=10)

        assert "Authentication required" in exc_info.value.message
        assert exc_info.value.data is not None
        assert exc_info.value.data["http_status"] == 401
        mock_client.get_trending_shows.assert_called_once_with(limit=10)
