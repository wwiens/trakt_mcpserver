"""Tests for the server.sync.tools module."""

import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from models.movies.movie import TraktMovie
from server.sync.tools import (
    add_user_ratings,
    fetch_user_ratings,
    remove_user_ratings,
)
from utils.api.error_types import TraktResourceNotFoundError
from utils.api.errors import InternalError

# Sample API response data from USER_RATINGS_DOC.MD
SAMPLE_USER_RATINGS_RESPONSE = [
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
]

SAMPLE_ADD_RATINGS_RESPONSE = {
    "added": {"movies": 1, "shows": 1, "seasons": 1, "episodes": 2},
    "not_found": {
        "movies": [{"rating": 10, "ids": {"imdb": "tt0000111"}}],
        "shows": [],
        "seasons": [],
        "episodes": [],
    },
}

SAMPLE_REMOVE_RATINGS_RESPONSE: dict[str, dict[str, int | list[dict[str, str]]]] = {
    "removed": {"movies": 2, "shows": 1, "seasons": 0, "episodes": 1},
    "not_found": {"movies": [], "shows": [], "seasons": [], "episodes": []},
}


@pytest.mark.asyncio
async def test_fetch_user_ratings_movies_success() -> None:
    """Test successful retrieval of user movie ratings."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock successful response - create proper Pydantic objects
        movie = TraktMovie(
            title="TRON: Legacy",
            year=2010,
            ids={
                "trakt": "1",
                "slug": "tron-legacy-2010",
                "imdb": "tt1104001",
                "tmdb": "20526",
            },
        )
        from models.sync.ratings import TraktSyncRating

        sample_ratings = [
            TraktSyncRating(
                rated_at="2014-09-01T09:10:11.000Z",
                rating=10,
                type="movie",
                movie=movie,
            )
        ]
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="movies")

        # Verify result contains formatted content
        assert "# Your Movies Ratings" in result
        assert "Found 1 rated movies" in result
        assert "TRON: Legacy (2010)" in result
        assert "Rating 10/10" in result

        # Verify client was called correctly
        mock_client.get_sync_ratings.assert_called_once_with("movies", None)


@pytest.mark.asyncio
async def test_fetch_user_ratings_with_rating_filter() -> None:
    """Test fetching user ratings with specific rating filter."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock response with only high-rated content
        movie = TraktMovie(
            title="TRON: Legacy",
            year=2010,
            ids={
                "trakt": "1",
                "slug": "tron-legacy-2010",
                "imdb": "tt1104001",
                "tmdb": "20526",
            },
        )
        from models.sync.ratings import TraktSyncRating

        high_rated_response = [
            TraktSyncRating(
                rated_at="2014-09-01T09:10:11.000Z",
                rating=10,
                type="movie",
                movie=movie,
            )
        ]
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(high_rated_response)
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="shows", rating=10)

        assert "# Your Shows Ratings (filtered to rating 10)" in result
        assert "Found 1 rated shows" in result

        # Verify client was called with rating filter
        mock_client.get_sync_ratings.assert_called_once_with("shows", 10)


@pytest.mark.asyncio
async def test_fetch_user_ratings_empty_result() -> None:
    """Test fetching user ratings when no ratings exist."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock empty response
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result([])
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="episodes")

        assert "# Your Episodes Ratings" in result
        assert "You haven't rated any episodes yet" in result

        mock_client.get_sync_ratings.assert_called_once_with("episodes", None)


@pytest.mark.asyncio
async def test_fetch_user_ratings_error_handling() -> None:
    """Test error handling in fetch_user_ratings."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock API error
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_exception(Exception("API error"))
        mock_client.get_sync_ratings.return_value = ratings_future

        with pytest.raises(InternalError) as exc_info:
            await fetch_user_ratings(rating_type="movies")

        assert "An unexpected error occurred" in str(exc_info.value)
        mock_client.get_sync_ratings.assert_called_once_with("movies", None)


@pytest.mark.asyncio
async def test_add_user_ratings_success() -> None:
    """Test successful addition of user ratings."""
    sample_items = [{"rating": 9, "title": "Inception", "imdb_id": "tt1375666"}]

    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock successful response - create proper Pydantic object
        from models.sync.ratings import (
            SyncRatingsNotFound,
            SyncRatingsSummary,
            SyncRatingsSummaryCount,
            TraktSyncRatingItem,
        )

        summary_response = SyncRatingsSummary(
            added=SyncRatingsSummaryCount(movies=1, shows=1, seasons=1, episodes=2),
            not_found=SyncRatingsNotFound(
                movies=[TraktSyncRatingItem(rating=10, ids={"imdb": "tt0000111"})],
                shows=[],
                seasons=[],
                episodes=[],
            ),
        )
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(summary_response)
        mock_client.add_sync_ratings.return_value = ratings_future

        result = await add_user_ratings(rating_type="movies", items=sample_items)

        # Verify result contains formatted summary
        assert "# Ratings Added - Movies" in result
        assert "Successfully added **1** movies rating(s)" in result
        assert "Movies: 1" in result
        assert "Shows: 1" in result

        # Verify client was called correctly
        mock_client.add_sync_ratings.assert_called_once()
        # Verify the request data structure
        call_args = mock_client.add_sync_ratings.call_args[0][0]
        assert hasattr(call_args, "movies")
        assert call_args.movies is not None
        assert len(call_args.movies) == 1


@pytest.mark.asyncio
async def test_add_user_ratings_validation_error() -> None:
    """Test add user ratings with invalid request data."""
    invalid_items = [
        {
            "rating": 15,  # Invalid rating (> 10)
            "imdb_id": "tt1375666",
        }
    ]

    # This should raise a validation error when creating UserRatingRequestItem
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        await add_user_ratings(rating_type="movies", items=invalid_items)


@pytest.mark.asyncio
async def test_add_user_ratings_api_error() -> None:
    """Test error handling in add_user_ratings."""
    sample_items = [{"rating": 9, "imdb_id": "tt1375666"}]

    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock API error
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_exception(Exception("API error"))
        mock_client.add_sync_ratings.return_value = ratings_future

        with pytest.raises(InternalError) as exc_info:
            await add_user_ratings(rating_type="movies", items=sample_items)

        assert "An unexpected error occurred" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_user_ratings_success() -> None:
    """Test successful removal of user ratings."""
    sample_items = [{"title": "Inception", "imdb_id": "tt1375666"}]

    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock successful response - create proper Pydantic object
        from models.sync.ratings import (
            SyncRatingsNotFound,
            SyncRatingsSummary,
            SyncRatingsSummaryCount,
        )

        summary_response = SyncRatingsSummary(
            removed=SyncRatingsSummaryCount(movies=2, shows=1, seasons=0, episodes=1),
            not_found=SyncRatingsNotFound(movies=[], shows=[], seasons=[], episodes=[]),
        )
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(summary_response)
        mock_client.remove_sync_ratings.return_value = ratings_future

        result = await remove_user_ratings(rating_type="movies", items=sample_items)

        # Verify result contains formatted summary
        assert "# Ratings Removed - Movies" in result
        assert "Successfully removed **2** movies rating(s)" in result
        assert "Movies: 2" in result
        assert "Shows: 1" in result
        assert "Episodes: 1" in result

        # Verify client was called correctly
        mock_client.remove_sync_ratings.assert_called_once()
        # Verify the request data structure
        call_args = mock_client.remove_sync_ratings.call_args[0][0]
        assert hasattr(call_args, "movies")
        assert call_args.movies is not None
        assert len(call_args.movies) == 1


@pytest.mark.asyncio
async def test_remove_user_ratings_with_not_found() -> None:
    """Test remove user ratings when some items are not found."""
    sample_items = [{"trakt_id": "123"}]

    # Response with not_found items (data moved to Pydantic object creation)

    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Create proper Pydantic object
        from models.sync.ratings import (
            SyncRatingsNotFound,
            SyncRatingsSummary,
            SyncRatingsSummaryCount,
            TraktSyncRatingItem,
        )

        summary_response = SyncRatingsSummary(
            removed=SyncRatingsSummaryCount(movies=0, shows=0, seasons=0, episodes=0),
            not_found=SyncRatingsNotFound(
                movies=[],
                shows=[TraktSyncRatingItem(ids={"trakt": "123"})],
                seasons=[],
                episodes=[],
            ),
        )
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(summary_response)
        mock_client.remove_sync_ratings.return_value = ratings_future

        result = await remove_user_ratings(rating_type="shows", items=sample_items)

        assert "# Ratings Removed - Shows" in result
        assert "No shows ratings were removed" in result
        assert "Items Not Found (1)" in result


@pytest.mark.asyncio
async def test_remove_user_ratings_api_error() -> None:
    """Test error handling in remove_user_ratings."""
    sample_items = [{"imdb_id": "tt1375666"}]

    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock API error
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_exception(
            TraktResourceNotFoundError("user", "ratings", "Not found")
        )
        mock_client.remove_sync_ratings.return_value = ratings_future

        with pytest.raises(TraktResourceNotFoundError):
            await remove_user_ratings(rating_type="movies", items=sample_items)


@pytest.mark.asyncio
async def test_all_tools_content_type_validation() -> None:
    """Test that content_type parameter is validated correctly."""
    # fetch_user_ratings should accept valid content types
    valid_types = ["movies", "shows", "seasons", "episodes"]

    for content_type in valid_types:
        with patch("server.sync.tools.SyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            ratings_future: asyncio.Future[Any] = asyncio.Future()
            ratings_future.set_result([])  # Empty list is fine as is
            mock_client.get_sync_ratings.return_value = ratings_future

            result = await fetch_user_ratings(rating_type=content_type)
            assert f"You haven't rated any {content_type} yet" in result
            mock_client.get_sync_ratings.assert_called_with(content_type, None)


@pytest.mark.asyncio
async def test_rating_parameter_validation() -> None:
    """Test that rating parameter is validated correctly."""
    valid_ratings = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for rating in valid_ratings:
        with patch("server.sync.tools.SyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            ratings_future: asyncio.Future[Any] = asyncio.Future()
            ratings_future.set_result([])  # Empty list is fine as is
            mock_client.get_sync_ratings.return_value = ratings_future

            result = await fetch_user_ratings(rating_type="movies", rating=rating)
            assert f"You haven't rated any movies yet with rating {rating}" in result
            mock_client.get_sync_ratings.assert_called_with("movies", rating)
