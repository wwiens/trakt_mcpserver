"""Tests for the server.sync.tools module."""

import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from models.movies.movie import TraktMovie
from models.sync.ratings import TraktSyncRating
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

        # Mock paginated response
        from models.types.pagination import (
            PaginatedResponse,
            PaginationMetadata,
        )

        pagination_metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=1
        )
        paginated_response = PaginatedResponse[TraktSyncRating](
            data=sample_ratings, pagination=pagination_metadata
        )

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(paginated_response)
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="movies")

        # Verify result contains formatted content
        assert "# Your Movies Ratings" in result
        assert "Found 1 rated movies on this page" in result
        assert "TRON: Legacy (2010)" in result
        assert "Rating 10/10" in result

        # Verify client was called correctly (no pagination when no page specified)
        mock_client.get_sync_ratings.assert_called_once_with(
            "movies", None, pagination=None
        )


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

        # Mock paginated response
        from models.types.pagination import (
            PaginatedResponse,
            PaginationMetadata,
        )

        pagination_metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=1
        )
        paginated_response = PaginatedResponse[TraktSyncRating](
            data=high_rated_response, pagination=pagination_metadata
        )

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(paginated_response)
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="shows", rating=10)

        assert "# Your Shows Ratings (filtered to rating 10)" in result
        assert "Found 1 rated shows on this page" in result

        # Verify client was called with rating filter (no pagination when no page specified)
        mock_client.get_sync_ratings.assert_called_once_with(
            "shows", 10, pagination=None
        )


@pytest.mark.asyncio
async def test_fetch_user_ratings_empty_result() -> None:
    """Test fetching user ratings when no ratings exist."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock empty paginated response
        from models.types.pagination import (
            PaginatedResponse,
            PaginationMetadata,
        )

        pagination_metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=0
        )
        empty_paginated_response = PaginatedResponse[TraktSyncRating](
            data=[], pagination=pagination_metadata
        )

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(empty_paginated_response)
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="episodes")

        assert "# Your Episodes Ratings" in result
        assert "You haven't rated any episodes yet" in result

        mock_client.get_sync_ratings.assert_called_once_with(
            "episodes", None, pagination=None
        )


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

        # Import here to avoid NameError

        mock_client.get_sync_ratings.assert_called_once_with(
            "movies", None, pagination=None
        )


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

            # Mock paginated response for empty results
            from models.types.pagination import PaginatedResponse, PaginationMetadata

            pagination_metadata = PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=0
            )
            empty_paginated_response = PaginatedResponse[TraktSyncRating](
                data=[], pagination=pagination_metadata
            )

            ratings_future: asyncio.Future[Any] = asyncio.Future()
            ratings_future.set_result(empty_paginated_response)
            mock_client.get_sync_ratings.return_value = ratings_future

            result = await fetch_user_ratings(rating_type=content_type)
            assert f"You haven't rated any {content_type} yet" in result

            # Import here to avoid NameError

            mock_client.get_sync_ratings.assert_called_with(
                content_type, None, pagination=None
            )


@pytest.mark.asyncio
async def test_rating_parameter_validation() -> None:
    """Test that rating parameter is validated correctly."""
    valid_ratings = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for rating in valid_ratings:
        with patch("server.sync.tools.SyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Mock paginated response for empty results
            from models.types.pagination import PaginatedResponse, PaginationMetadata

            pagination_metadata = PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=0
            )
            empty_paginated_response = PaginatedResponse[TraktSyncRating](
                data=[], pagination=pagination_metadata
            )

            ratings_future: asyncio.Future[Any] = asyncio.Future()
            ratings_future.set_result(empty_paginated_response)
            mock_client.get_sync_ratings.return_value = ratings_future

            result = await fetch_user_ratings(rating_type="movies", rating=rating)
            assert f"You haven't rated any movies yet with rating {rating}" in result

            # Import here to avoid NameError

            mock_client.get_sync_ratings.assert_called_with(
                "movies", rating, pagination=None
            )


# Pagination tests
@pytest.mark.asyncio
async def test_fetch_user_ratings_paginated_success() -> None:
    """Test successful retrieval of paginated user ratings."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock successful paginated response
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
        from models.types.pagination import PaginatedResponse, PaginationMetadata

        sample_ratings = [
            TraktSyncRating(
                rated_at="2014-09-01T09:10:11.000Z",
                rating=10,
                type="movie",
                movie=movie,
            )
        ]

        pagination_metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=3, total_items=25
        )

        paginated_response = PaginatedResponse[TraktSyncRating](
            data=sample_ratings, pagination=pagination_metadata
        )

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(paginated_response)
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="movies", page=1)

        # Verify result contains paginated content
        assert "# Your Movies Ratings" in result
        assert "📄 **Page 1 of 3" in result
        assert "items 1-1 of 25" in result
        assert "📍 **Navigation:** Next: page 2" in result
        assert "Found 1 rated movies on this page" in result
        assert "TRON: Legacy (2010)" in result

        # Verify paginated client method was called
        mock_client.get_sync_ratings.assert_called_once()
        args, kwargs = mock_client.get_sync_ratings.call_args
        assert args[0] == "movies"
        assert args[1] is None  # rating filter
        assert "pagination" in kwargs
        pagination_params = kwargs["pagination"]
        assert pagination_params.page == 1
        assert pagination_params.limit == 100  # test limit


@pytest.mark.asyncio
async def test_fetch_user_ratings_paginated_with_filter() -> None:
    """Test paginated user ratings with rating filter."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock paginated response with rating filter
        movie = TraktMovie(
            title="The Dark Knight",
            year=2008,
            ids={
                "trakt": "6",
                "slug": "the-dark-knight-2008",
                "imdb": "tt0468569",
                "tmdb": "155",
            },
        )
        from models.sync.ratings import TraktSyncRating
        from models.types.pagination import PaginatedResponse, PaginationMetadata

        sample_ratings = [
            TraktSyncRating(
                rated_at="2014-09-01T09:10:11.000Z",
                rating=10,
                type="movie",
                movie=movie,
            )
        ]

        pagination_metadata = PaginationMetadata(
            current_page=2, items_per_page=5, total_pages=2, total_items=8
        )

        paginated_response = PaginatedResponse[TraktSyncRating](
            data=sample_ratings, pagination=pagination_metadata
        )

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(paginated_response)
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="movies", rating=10, page=2)

        # Verify result contains paginated content with rating filter
        assert "# Your Movies Ratings (filtered to rating 10)" in result
        assert "📄 **Page 2 of 2" in result
        assert "📍 **Navigation:** Previous: page 1" in result
        assert "The Dark Knight (2008)" in result

        # Verify paginated client method was called with rating filter
        mock_client.get_sync_ratings.assert_called_once()
        args, kwargs = mock_client.get_sync_ratings.call_args
        assert args[0] == "movies"
        assert args[1] == 10  # rating filter
        pagination_params = kwargs["pagination"]
        assert pagination_params.page == 2


@pytest.mark.asyncio
async def test_fetch_user_ratings_paginated_empty_result() -> None:
    """Test paginated user ratings with empty results."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock empty paginated response
        from models.types.pagination import PaginatedResponse, PaginationMetadata

        pagination_metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=0
        )

        paginated_response = PaginatedResponse[TraktSyncRating](
            data=[], pagination=pagination_metadata
        )

        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_result(paginated_response)
        mock_client.get_sync_ratings.return_value = ratings_future

        result = await fetch_user_ratings(rating_type="shows", page=1)

        # Verify result contains paginated empty state
        assert "# Your Shows Ratings" in result
        assert "You haven't rated any shows yet" in result
        assert "📄 **Pagination Info:** 0 total items" in result

        # Verify paginated client method was called
        mock_client.get_sync_ratings.assert_called_once()


@pytest.mark.asyncio
# REMOVED: Test for backward compatibility that no longer exists after cleanup


@pytest.mark.asyncio
async def test_fetch_user_ratings_paginated_error_handling() -> None:
    """Test error handling in paginated user ratings retrieval."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock API error in paginated request
        ratings_future: asyncio.Future[Any] = asyncio.Future()
        ratings_future.set_exception(Exception("API error"))
        mock_client.get_sync_ratings.return_value = ratings_future

        with pytest.raises(InternalError) as exc_info:
            await fetch_user_ratings(rating_type="movies", page=1)

        assert "An unexpected error occurred" in str(exc_info.value)
        mock_client.get_sync_ratings.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_ratings_page_parameter_validation() -> None:
    """Test that page parameter is validated correctly."""
    with patch("server.sync.tools.SyncClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Valid page numbers should work
        valid_pages = [1, 2, 5, 10, 100]

        for page_num in valid_pages:
            from models.types.pagination import (
                PaginatedResponse,
                PaginationMetadata,
            )

            pagination_metadata = PaginationMetadata(
                current_page=page_num,
                items_per_page=10,
                total_pages=100,
                total_items=1000,
            )

            paginated_response = PaginatedResponse[TraktSyncRating](
                data=[], pagination=pagination_metadata
            )

            ratings_future: asyncio.Future[Any] = asyncio.Future()
            ratings_future.set_result(paginated_response)
            mock_client.get_sync_ratings.return_value = ratings_future

            result = await fetch_user_ratings(rating_type="movies", page=page_num)
            assert f"Page {page_num} of 100" in result

        # Invalid page numbers should raise validation error
        from pydantic import ValidationError

        invalid_pages = [0, -1, -10]
        for invalid_page in invalid_pages:
            with pytest.raises(ValidationError):
                await fetch_user_ratings(rating_type="movies", page=invalid_page)
