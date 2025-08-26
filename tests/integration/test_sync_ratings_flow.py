"""Integration tests for the sync ratings flow."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from client.sync.client import SyncClient
from models.auth.auth import TraktAuthToken

# TYPE_CHECKING imports removed as not actually used in runtime


# Sample API response data from USER_RATINGS_DOC.MD
SAMPLE_USER_RATINGS_RESPONSE: list[dict[str, Any]] = [
    {
        "rated_at": "2014-09-01T09:10:11.000Z",
        "rating": 10,
        "type": "movie",
        "movie": {
            "title": "TRON: Legacy",
            "year": 2010,
            "ids": {
                "trakt": "1",
                "slug": "tron-legacy-2010",
                "imdb": "tt1104001",
                "tmdb": "20526",
            },
        },
    },
    {
        "rated_at": "2014-09-01T09:10:11.000Z",
        "rating": 8,
        "type": "show",
        "show": {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {
                "trakt": "1",
                "slug": "breaking-bad",
                "tvdb": "81189",
                "imdb": "tt0903747",
                "tmdb": "1396",
            },
        },
    },
    {
        "rated_at": "2014-09-01T09:10:11.000Z",
        "rating": 6,
        "type": "episode",
        "episode": {
            "season": 1,
            "number": 1,
            "title": "Pilot",
            "ids": {
                "trakt": "1",
                "tvdb": "2639411",
                "imdb": "tt1683084",
                "tmdb": "62118",
            },
        },
        "show": {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {
                "trakt": "1",
                "slug": "breaking-bad",
                "tvdb": "81189",
                "imdb": "tt0903747",
                "tmdb": "1396",
            },
        },
    },
]

SAMPLE_ADD_RATINGS_RESPONSE: dict[str, Any] = {
    "added": {"movies": 1, "shows": 1, "seasons": 0, "episodes": 2},
    "not_found": {
        "movies": [{"rating": 10, "ids": {"imdb": "tt0000111"}}],
        "shows": [],
        "seasons": [],
        "episodes": [],
    },
}

SAMPLE_REMOVE_RATINGS_RESPONSE: dict[str, Any] = {
    "removed": {"movies": 2, "shows": 1, "seasons": 0, "episodes": 1},
    "not_found": {"movies": [], "shows": [], "seasons": [], "episodes": []},
}


@pytest.mark.asyncio
async def test_fetch_user_ratings_integration() -> None:
    """Test complete flow from server tool to client for fetching user ratings."""

    # Set up mock HTTP responses
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Configure the mock HTTP client
        mock_instance = mock_client.return_value.__aenter__.return_value

        # Mock for ratings request
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = SAMPLE_USER_RATINGS_RESPONSE
        ratings_mock.raise_for_status = MagicMock()

        mock_instance.get.return_value = ratings_mock

        # Create authenticated sync client
        sync_client = SyncClient()
        sync_client.auth_token = TraktAuthToken(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import fetch_user_ratings

            # Test fetching all movies
            result = await fetch_user_ratings(rating_type="movies")

            # Verify the formatted response
            assert "# Your Movies Ratings" in result
            assert "movies" in result
            assert "TRON: Legacy (2010)" in result
            assert "Rating 10/10" in result

            # Verify the HTTP request was made correctly
            mock_instance.get.assert_called()
            call_args = mock_instance.get.call_args[0]
            assert "/sync/ratings/movies" in call_args[0]


@pytest.mark.asyncio
async def test_fetch_user_ratings_with_rating_filter_integration() -> None:
    """Test fetching user ratings with rating filter through complete stack."""

    # Filter for only shows with rating 8
    high_rated_response = [
        r
        for r in SAMPLE_USER_RATINGS_RESPONSE
        if r["rating"] == 8 and r["type"] == "show"
    ]

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = mock_client.return_value.__aenter__.return_value

        ratings_mock = MagicMock()
        ratings_mock.json.return_value = high_rated_response
        ratings_mock.raise_for_status = MagicMock()

        mock_instance.get.return_value = ratings_mock

        sync_client = SyncClient()
        sync_client.auth_token = TraktAuthToken(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="shows", rating=8)

            # Verify rating-specific formatting
            assert "# Your Shows Ratings (filtered to rating 8)" in result
            assert "shows" in result
            assert "TRON: Legacy" not in result  # Should only show rated=8 content

            # Verify the correct API endpoint was called with rating filter
            mock_instance.get.assert_called()
            call_args = mock_instance.get.call_args[0]
            assert "/sync/ratings/shows/8" in call_args[0]


@pytest.mark.asyncio
async def test_add_user_ratings_integration() -> None:
    """Test complete flow for adding user ratings."""

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = mock_client.return_value.__aenter__.return_value

        # Mock for add ratings POST request
        add_mock = MagicMock()
        add_mock.json.return_value = SAMPLE_ADD_RATINGS_RESPONSE
        add_mock.raise_for_status = MagicMock()

        mock_instance.post.return_value = add_mock

        sync_client = SyncClient()
        sync_client.auth_token = TraktAuthToken(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import add_user_ratings

            # Sample request data - using flat structure
            sample_items = [{"rating": 9, "title": "Inception", "imdb_id": "tt1375666"}]

            result = await add_user_ratings(rating_type="movies", items=sample_items)

            # Verify the formatted response
            assert "# Ratings Added - Movies" in result
            assert "Successfully added **1** movies rating(s)" in result
            assert "Movies: 1" in result
            assert "Shows: 1" in result
            assert "Episodes: 2" in result

            # Verify the POST request was made correctly
            mock_instance.post.assert_called()
            call_args = mock_instance.post.call_args
            assert "/sync/ratings" in call_args[0][0]  # endpoint
            assert "json" in call_args[1]  # request data


@pytest.mark.asyncio
async def test_remove_user_ratings_integration() -> None:
    """Test complete flow for removing user ratings."""

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = mock_client.return_value.__aenter__.return_value

        # Mock for remove ratings DELETE request
        remove_mock = MagicMock()
        remove_mock.json.return_value = SAMPLE_REMOVE_RATINGS_RESPONSE
        remove_mock.raise_for_status = MagicMock()

        mock_instance.request.return_value = remove_mock

        sync_client = SyncClient()
        sync_client.auth_token = TraktAuthToken(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import remove_user_ratings

            # Sample request data (no rating needed for removal) - using flat structure
            sample_items = [{"title": "Inception", "imdb_id": "tt1375666"}]

            result = await remove_user_ratings(rating_type="movies", items=sample_items)

            # Verify the formatted response
            assert "# Ratings Removed - Movies" in result
            assert "Successfully removed **2** movies rating(s)" in result
            assert "Movies: 2" in result
            assert "Shows: 1" in result
            assert "Episodes: 1" in result

            # Verify the DELETE request was made correctly
            mock_instance.request.assert_called()
            call_args = mock_instance.request.call_args
            assert call_args[1]["method"] == "DELETE"  # HTTP method
            assert "/sync/ratings" in call_args[1]["url"]  # endpoint
            assert "json" in call_args[1]  # request data


@pytest.mark.asyncio
async def test_authentication_flow_integration() -> None:
    """Test that sync ratings operations require authentication."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create unauthenticated sync client
        sync_client = SyncClient()
        # No auth_token set - should be unauthenticated
        sync_client.is_authenticated = lambda: False

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import (
                add_user_ratings,
                fetch_user_ratings,
                remove_user_ratings,
            )

            # All operations should raise authentication errors

            with pytest.raises(
                ValueError,
                match="You must be authenticated to access your personal ratings",
            ):
                await fetch_user_ratings(rating_type="movies")

            with pytest.raises(
                ValueError, match="You must be authenticated to add personal ratings"
            ):
                await add_user_ratings(
                    rating_type="movies", items=[{"rating": 10, "imdb_id": "tt1375666"}]
                )

            with pytest.raises(
                ValueError, match="You must be authenticated to remove personal ratings"
            ):
                await remove_user_ratings(
                    rating_type="movies", items=[{"imdb_id": "tt1375666"}]
                )


@pytest.mark.asyncio
async def test_error_propagation_integration() -> None:
    """Test error propagation through the complete sync ratings stack."""

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Configure mock to raise HTTP errors
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get.side_effect = Exception("API connection error")

        sync_client = SyncClient()
        sync_client.auth_token = TraktAuthToken(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import fetch_user_ratings
            from utils.api.errors import InternalError

            # Should raise InternalError for unexpected exceptions
            with pytest.raises(InternalError) as exc_info:
                await fetch_user_ratings(rating_type="movies")

            assert "unexpected error occurred" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_empty_ratings_response_integration() -> None:
    """Test handling of empty ratings response through complete stack."""

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = mock_client.return_value.__aenter__.return_value

        # Mock empty response
        empty_mock = MagicMock()
        empty_mock.json.return_value = []  # Empty ratings list
        empty_mock.raise_for_status = MagicMock()

        mock_instance.get.return_value = empty_mock

        sync_client = SyncClient()
        sync_client.auth_token = TraktAuthToken(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="episodes")

            # Verify empty state is handled gracefully
            assert "# Your Episodes Ratings" in result
            assert "You haven't rated any episodes yet" in result


@pytest.mark.asyncio
async def test_mixed_content_types_integration() -> None:
    """Test fetching ratings for different content types in sequence."""

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = mock_client.return_value.__aenter__.return_value

        # Mock different responses for different content types
        movies_response = [
            r for r in SAMPLE_USER_RATINGS_RESPONSE if r["type"] == "movie"
        ]
        shows_response = [
            r for r in SAMPLE_USER_RATINGS_RESPONSE if r["type"] == "show"
        ]
        episodes_response = [
            r for r in SAMPLE_USER_RATINGS_RESPONSE if r["type"] == "episode"
        ]

        def mock_get_side_effect(url: str, **kwargs: Any) -> MagicMock:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()

            if "/movies" in url:
                mock_response.json.return_value = movies_response
            elif "/shows" in url:
                mock_response.json.return_value = shows_response
            elif "/episodes" in url:
                mock_response.json.return_value = episodes_response
            else:
                mock_response.json.return_value = []

            return mock_response

        mock_instance.get.side_effect = mock_get_side_effect

        sync_client = SyncClient()
        sync_client.auth_token = TraktAuthToken(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import fetch_user_ratings

            # Test movies
            movie_result = await fetch_user_ratings(rating_type="movies")
            assert "TRON: Legacy" in movie_result
            assert "Breaking Bad" not in movie_result

            # Test shows
            show_result = await fetch_user_ratings(rating_type="shows")
            assert "Breaking Bad" in show_result
            assert "TRON: Legacy" not in show_result

            # Test episodes
            episode_result = await fetch_user_ratings(rating_type="episodes")
            assert "Breaking Bad" in episode_result
            assert "Rating 6/10" in episode_result


@pytest.mark.asyncio
async def test_rating_grouping_integration() -> None:
    """Test that ratings are properly grouped by score in formatted output."""

    # Create ratings with different scores for grouping test
    mixed_ratings_response = [
        {
            "rated_at": "2014-09-01T09:10:11.000Z",
            "rating": 10,
            "type": "movie",
            "movie": {"title": "Movie A", "year": 2020, "ids": {"trakt": "1"}},
        },
        {
            "rated_at": "2014-09-01T09:10:11.000Z",
            "rating": 10,
            "type": "movie",
            "movie": {"title": "Movie B", "year": 2021, "ids": {"trakt": "2"}},
        },
        {
            "rated_at": "2014-09-01T09:10:11.000Z",
            "rating": 8,
            "type": "movie",
            "movie": {"title": "Movie C", "year": 2022, "ids": {"trakt": "3"}},
        },
    ]

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = mock_client.return_value.__aenter__.return_value

        ratings_mock = MagicMock()
        ratings_mock.json.return_value = mixed_ratings_response
        ratings_mock.raise_for_status = MagicMock()

        mock_instance.get.return_value = ratings_mock

        sync_client = SyncClient()
        sync_client.auth_token = TraktAuthToken(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="movies")

            # Verify ratings are grouped by score
            assert "## Rating 10/10 (2 movies)" in result
            assert "## Rating 8/10 (1 movies)" in result
            assert "Movie A (2020)" in result
            assert "Movie B (2021)" in result
            assert "Movie C (2022)" in result

            # Verify grouping order (highest ratings first)
            pos_10 = result.find("## Rating 10/10")
            pos_8 = result.find("## Rating 8/10")
            assert pos_10 < pos_8  # 10/10 should come before 8/10
