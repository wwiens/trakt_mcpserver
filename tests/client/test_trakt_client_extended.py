import os
import time
from unittest.mock import MagicMock, patch

import pytest

from models import TraktAuthToken
from trakt_client import TraktClient


@pytest.mark.asyncio
async def test_search_shows():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "type": "show",
            "score": 100.0,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": "1", "slug": "breaking-bad"},
            },
        },
        {
            "type": "show",
            "score": 80.0,
            "show": {
                "title": "Better Call Saul",
                "year": 2015,
                "ids": {"trakt": "2", "slug": "better-call-saul"},
            },
        },
    ]
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = TraktClient()
        result = await client.search_shows(query="breaking", limit=2)

        assert len(result) == 2
        assert result[0]["show"]["title"] == "Breaking Bad"
        assert result[1]["show"]["title"] == "Better Call Saul"

        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]
        call_kwargs = mock_client.return_value.__aenter__.return_value.get.call_args[1]

        assert "/search/show" in call_args
        assert call_kwargs["params"]["query"] == "breaking"
        assert call_kwargs["params"]["limit"] == 2


@pytest.mark.asyncio
async def test_search_movies():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "type": "movie",
            "score": 100.0,
            "movie": {
                "title": "Inception",
                "year": 2010,
                "ids": {"trakt": "1", "slug": "inception-2010"},
            },
        },
        {
            "type": "movie",
            "score": 80.0,
            "movie": {
                "title": "Interstellar",
                "year": 2014,
                "ids": {"trakt": "2", "slug": "interstellar-2014"},
            },
        },
    ]
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = TraktClient()
        result = await client.search_movies(query="inter", limit=2)

        assert len(result) == 2
        assert result[0]["movie"]["title"] == "Inception"
        assert result[1]["movie"]["title"] == "Interstellar"

        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]
        call_kwargs = mock_client.return_value.__aenter__.return_value.get.call_args[1]

        assert "/search/movie" in call_args
        assert call_kwargs["params"]["query"] == "inter"
        assert call_kwargs["params"]["limit"] == 2


@pytest.mark.asyncio
async def test_get_show_comments():
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "123",
            "comment": "This show is amazing!",
            "spoiler": False,
            "review": False,
            "likes": 10,
            "replies": 2,
            "created_at": "2023-01-15T20:30:00Z",
            "user": {"username": "testuser"},
        }
    ]
    mock_response.raise_for_status = MagicMock()

    # Patch the AsyncClient to return our mock response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = TraktClient()
        result = await client.get_show_comments(show_id="1", limit=10, sort="newest")

        assert len(result) == 1
        assert result[0]["comment"] == "This show is amazing!"
        assert result[0]["user"]["username"] == "testuser"

        # Verify the correct endpoint was called
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]

        assert "/shows/1/comments/newest" in call_args


@pytest.mark.asyncio
async def test_get_movie_comments():
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "456",
            "comment": "Great movie!",
            "spoiler": False,
            "review": True,
            "likes": 15,
            "replies": 3,
            "created_at": "2023-02-20T15:45:00Z",
            "user": {"username": "moviefan"},
        }
    ]
    mock_response.raise_for_status = MagicMock()

    # Patch the AsyncClient to return our mock response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = TraktClient()
        result = await client.get_movie_comments(movie_id="1", limit=10, sort="likes")

        assert len(result) == 1
        assert result[0]["comment"] == "Great movie!"
        assert result[0]["user"]["username"] == "moviefan"
        assert result[0]["review"]

        # Verify the correct endpoint was called
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]

        assert "/movies/1/comments/likes" in call_args


@pytest.mark.asyncio
async def test_get_comment_replies():
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "789",
            "comment": "I agree with your review!",
            "spoiler": False,
            "review": False,
            "likes": 5,
            "created_at": "2023-02-21T10:30:00Z",
            "user": {"username": "replier"},
        }
    ]
    mock_response.raise_for_status = MagicMock()

    # Patch the AsyncClient to return our mock response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = TraktClient()
        result = await client.get_comment_replies(
            comment_id="456", limit=10, sort="newest"
        )

        assert len(result) == 1
        assert result[0]["comment"] == "I agree with your review!"
        assert result[0]["user"]["username"] == "replier"

        # Verify the correct endpoint was called
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]

        assert "/comments/456/replies/newest" in call_args


@pytest.mark.asyncio
async def test_get_show_ratings():
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "rating": 8.5,
        "votes": 1000,
        "distribution": {
            "10": 200,
            "9": 300,
            "8": 250,
            "7": 150,
            "6": 50,
            "5": 30,
            "4": 10,
            "3": 5,
            "2": 3,
            "1": 2,
        },
    }
    mock_response.raise_for_status = MagicMock()

    # Patch the AsyncClient to return our mock response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = TraktClient()
        result = await client.get_show_ratings(show_id="1")

        assert result["rating"] == 8.5
        assert result["votes"] == 1000
        assert result["distribution"]["10"] == 200

        # Verify the correct endpoint was called
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]

        assert "/shows/1/ratings" in call_args


@pytest.mark.asyncio
async def test_get_movie_ratings():
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = {
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
    mock_response.raise_for_status = MagicMock()

    # Patch the AsyncClient to return our mock response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = TraktClient()
        result = await client.get_movie_ratings(movie_id="1")

        assert result["rating"] == 9.0
        assert result["votes"] == 2000
        assert result["distribution"]["10"] == 800

        # Verify the correct endpoint was called
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]

        assert "/movies/1/ratings" in call_args


@pytest.mark.asyncio
async def test_checkin_to_show():
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "sharing": {"twitter": False, "mastodon": False, "tumblr": False},
        "show": {"title": "Breaking Bad", "year": 2008},
        "episode": {"season": 1, "number": 1, "title": "Pilot"},
    }
    mock_response.raise_for_status = MagicMock()

    # Patch the AsyncClient to return our mock response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        client = TraktClient()
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        result = await client.checkin_to_show(
            episode_season=1, episode_number=1, show_id="1"
        )

        assert result["id"] == 123456
        assert result["show"]["title"] == "Breaking Bad"
        assert result["episode"]["season"] == 1
        assert result["episode"]["number"] == 1

        # Verify the correct endpoint was called with the right data
        mock_client.return_value.__aenter__.return_value.post.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args[0][
            0
        ]
        call_kwargs = mock_client.return_value.__aenter__.return_value.post.call_args[1]

        assert "/checkin" in call_args
        assert call_kwargs["json"]["episode"]["season"] == 1
        assert call_kwargs["json"]["episode"]["number"] == 1
        assert call_kwargs["json"]["show"]["ids"]["trakt"] == "1"


@pytest.mark.asyncio
async def test_checkin_to_show_with_title():
    # Mock the httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "show": {"title": "Breaking Bad", "year": 2008},
        "episode": {"season": 1, "number": 1, "title": "Pilot"},
    }
    mock_response.raise_for_status = MagicMock()

    # Patch the AsyncClient to return our mock response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        # Create a client with a mock auth token
        client = TraktClient()
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        # Test checking in with show title and year
        result = await client.checkin_to_show(
            episode_season=1,
            episode_number=1,
            show_title="Breaking Bad",
            show_year=2008,
            message="Watching this again!",
            share_twitter=True,
        )

        assert result["id"] == 123456
        assert result["show"]["title"] == "Breaking Bad"

        # Verify the correct endpoint was called with the right data
        mock_client.return_value.__aenter__.return_value.post.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args[0][
            0
        ]
        call_kwargs = mock_client.return_value.__aenter__.return_value.post.call_args[1]

        assert "/checkin" in call_args
        assert call_kwargs["json"]["episode"]["season"] == 1
        assert call_kwargs["json"]["episode"]["number"] == 1
        assert call_kwargs["json"]["show"]["title"] == "Breaking Bad"
        assert call_kwargs["json"]["show"]["year"] == 2008
        assert call_kwargs["json"]["message"] == "Watching this again!"
        assert call_kwargs["json"]["sharing"]["twitter"]


@pytest.mark.asyncio
async def test_checkin_to_show_not_authenticated():
    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create a client without an auth token
        client = TraktClient()

        # Test checking in without authentication
        # The handle_api_errors decorator will catch the ValueError and return an error message
        result = await client.checkin_to_show(
            episode_season=1, episode_number=1, show_id="1"
        )

        # Check that the function returned an error message
        assert (
            "Error: An unexpected error occurred: You must be authenticated to check in to a show"
            in result
        )


@pytest.mark.asyncio
async def test_checkin_to_show_missing_info():
    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create a client with a mock auth token
        client = TraktClient()
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        # Test checking in without show ID or title
        # The handle_api_errors decorator will catch the ValueError and return an error message
        result = await client.checkin_to_show(episode_season=1, episode_number=1)

        # Check that the function returned an error message
        assert (
            "Error: An unexpected error occurred: Either show_id or show_title must be provided"
            in result
        )


# Test removed as refresh_token method doesn't exist in TraktClient

# Test removed as refresh_token method doesn't exist in TraktClient

# Test removed as is_token_expiring_soon method doesn't exist in TraktClient


@pytest.mark.asyncio
async def test_clear_auth_token():
    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
        patch("os.path.exists", return_value=True),
        patch("os.remove") as mock_remove,
    ):
        client = TraktClient()
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )
        client.headers["Authorization"] = "Bearer test_token"

        result = client.clear_auth_token()

        # Check that the token was cleared
        assert result is True
        assert client.auth_token is None
        assert "Authorization" not in client.headers
        mock_remove.assert_called_once_with("auth_token.json")

        client.auth_token = None
        result = client.clear_auth_token()
        assert result is False
