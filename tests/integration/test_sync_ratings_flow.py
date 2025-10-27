"""Integration tests for the sync ratings flow."""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.sync.client import SyncClient

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
async def test_fetch_user_ratings_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test complete flow from server tool to client for fetching user ratings."""

    # Set up mock HTTP responses
    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Mock for ratings request
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = SAMPLE_USER_RATINGS_RESPONSE
        ratings_mock.raise_for_status = MagicMock()
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=ratings_mock)
        mock_http_client.aclose = AsyncMock()
        # Patch the client's _get_client method to return our mock
        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            # Test fetching all movies
            result = await fetch_user_ratings(rating_type="movies")
            # Verify the formatted response
            assert "# Your Movies Ratings" in result
            assert "movies" in result
            assert "TRON: Legacy (2010)" in result
            assert "Rating 10/10" in result

            # Verify the HTTP request was made correctly
            mock_http_client.get.assert_called()
            call_args = mock_http_client.get.call_args[0]
            assert "/sync/ratings/movies" in call_args[0]


@pytest.mark.asyncio
async def test_fetch_user_ratings_with_rating_filter_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test fetching user ratings with rating filter through complete stack."""

    # Filter for only shows with rating 8
    high_rated_response = [
        r
        for r in SAMPLE_USER_RATINGS_RESPONSE
        if r["rating"] == 8 and r["type"] == "show"
    ]

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = high_rated_response
        ratings_mock.raise_for_status = MagicMock()
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=ratings_mock)
        mock_http_client.aclose = AsyncMock()
        # Patch the client's _get_client method to return our mock
        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="shows", rating=8)
            # Verify rating-specific formatting
            assert "# Your Shows Ratings (filtered to rating 8)" in result
            assert "show" in result
            assert "TRON: Legacy" not in result  # Should only show rated=8 content

            # Verify the correct API endpoint was called with rating filter
            mock_http_client.get.assert_called()
            call_args = mock_http_client.get.call_args[0]
            assert "/sync/ratings/shows/8" in call_args[0]


@pytest.mark.asyncio
async def test_add_user_ratings_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test complete flow for adding user ratings."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Mock for add ratings POST request
        add_mock = MagicMock()
        add_mock.json.return_value = SAMPLE_ADD_RATINGS_RESPONSE
        add_mock.raise_for_status = MagicMock()
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=add_mock)
        mock_http_client.aclose = AsyncMock()
        # Patch the client's _get_client method to return our mock
        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
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
            mock_http_client.post.assert_called()
            call_args = mock_http_client.post.call_args
            assert "/sync/ratings" in call_args[0][0]  # endpoint
            assert "json" in call_args[1]  # request data


@pytest.mark.asyncio
async def test_remove_user_ratings_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test complete flow for removing user ratings."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.post = AsyncMock()
        # Mock for remove ratings POST request
        remove_mock = MagicMock()
        remove_mock.json.return_value = SAMPLE_REMOVE_RATINGS_RESPONSE
        remove_mock.raise_for_status = MagicMock()
        mock_http_client.post.return_value = remove_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
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

            # Verify the POST request was made correctly
            mock_http_client.post.assert_called()
            call_args = mock_http_client.post.call_args
            assert "/sync/ratings/remove" in call_args[0][0]  # endpoint
            assert "json" in call_args[1]  # request data


@pytest.mark.asyncio
async def test_authentication_flow_integration(
    authenticated_sync_client: SyncClient,
) -> None:
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
async def test_error_propagation_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test error propagation through the complete sync ratings stack."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Configure mock to raise HTTP errors
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        mock_http_client.get.side_effect = Exception("API connection error")

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings
            from utils.api.errors import InternalError

            # Should raise InternalError for unexpected exceptions
            with pytest.raises(InternalError) as exc_info:
                await fetch_user_ratings(rating_type="movies")

            assert "unexpected error occurred" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_empty_ratings_response_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test handling of empty ratings response through complete stack."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        # Mock empty response
        empty_mock = MagicMock()
        empty_mock.json.return_value = []  # Empty ratings list
        empty_mock.raise_for_status = MagicMock()
        mock_http_client.get.return_value = empty_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="episodes")
            # Verify empty state is handled gracefully
            assert "# Your Episodes Ratings" in result
            assert "You haven't rated any episodes yet" in result


@pytest.mark.asyncio
async def test_mixed_content_types_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test fetching ratings for different content types in sequence."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
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

        mock_http_client.get.side_effect = mock_get_side_effect

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
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
async def test_rating_grouping_integration(
    authenticated_sync_client: SyncClient,
) -> None:
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

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = mixed_ratings_response
        ratings_mock.raise_for_status = MagicMock()
        mock_http_client.get.return_value = ratings_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="movies")
            # Verify ratings are grouped by score
            assert "## Rating 10/10 (2 movies)" in result
            assert "## Rating 8/10 (1 movie)" in result
            assert "Movie A (2020)" in result
            assert "Movie B (2021)" in result
            assert "Movie C (2022)" in result

            # Verify grouping order (highest ratings first)
            pos_10 = result.find("## Rating 10/10")
            pos_8 = result.find("## Rating 8/10")
            assert pos_10 < pos_8  # 10/10 should come before 8/10


# Pagination integration tests
@pytest.mark.asyncio
async def test_fetch_user_ratings_paginated_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test complete flow for paginated user ratings fetching."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Mock paginated response - first page of results
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = SAMPLE_USER_RATINGS_RESPONSE[
            :2
        ]  # First 2 items
        ratings_mock.raise_for_status = MagicMock()
        # Mock pagination headers
        ratings_mock.headers = {
            "X-Pagination-Page": "1",
            "X-Pagination-Limit": "2",
            "X-Pagination-Page-Count": "2",
            "X-Pagination-Item-Count": "3",
        }

        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = ratings_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            # Test fetching page 1 of movies
            result = await fetch_user_ratings(rating_type="movies", page=1)
            # Verify paginated response format
            assert "# Your Movies Ratings" in result
            assert "📄 **Page 1 of 2" in result
            assert "items 1-2 of 3" in result  # 2 items on this page
            assert "📍 **Navigation:** Next: page 2" in result
            assert "Found 2 rated movies on this page" in result
            assert "TRON: Legacy (2010)" in result

            # Verify the HTTP request was made correctly with page parameter
            mock_http_client.get.assert_called()
            call_args = mock_http_client.get.call_args
            call_kwargs = call_args[1]
            assert "params" in call_kwargs
            assert call_kwargs["params"]["page"] == 1
            from config.api import DEFAULT_LIMIT

            assert (
                call_kwargs["params"]["limit"] == DEFAULT_LIMIT
            )  # uses DEFAULT_LIMIT when page specified
            assert "/sync/ratings/movies" in call_args[0][0]


@pytest.mark.asyncio
async def test_fetch_user_ratings_paginated_last_page_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test paginated user ratings on the last page (no next page navigation)."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        # Mock last page response
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = SAMPLE_USER_RATINGS_RESPONSE[2:]  # Last item
        ratings_mock.raise_for_status = MagicMock()
        # Mock pagination headers for last page
        ratings_mock.headers = {
            "X-Pagination-Page": "2",
            "X-Pagination-Limit": "2",
            "X-Pagination-Page-Count": "2",
            "X-Pagination-Item-Count": "3",
        }

        mock_http_client.get.return_value = ratings_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="episodes", page=2)
            # Verify last page pagination formatting
            assert "# Your Episodes Ratings" in result
            assert "📄 **Page 2 of 2" in result
            assert "📍 **Navigation:** Previous: page 1" in result
            # Should NOT have "Next: page" text
            assert "Next: page" not in result
            assert "Found 1 rated episode on this page" in result

            # Verify page parameter was sent correctly
            call_args = mock_http_client.get.call_args
            assert call_args[1]["params"]["page"] == 2


@pytest.mark.asyncio
async def test_fetch_user_ratings_paginated_with_rating_filter_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test paginated user ratings with rating filter through complete stack."""

    # Filter response to only rating=10 content
    high_rated_response = [r for r in SAMPLE_USER_RATINGS_RESPONSE if r["rating"] == 10]

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = high_rated_response
        ratings_mock.raise_for_status = MagicMock()
        # Mock pagination headers for filtered results
        ratings_mock.headers = {
            "X-Pagination-Page": "1",
            "X-Pagination-Limit": "10",
            "X-Pagination-Page-Count": "1",
            "X-Pagination-Item-Count": "1",
        }

        mock_http_client.get.return_value = ratings_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="movies", rating=10, page=1)
            # Verify paginated response with rating filter
            assert "# Your Movies Ratings (filtered to rating 10)" in result
            assert "📄 **1 total items" in result  # Single page format
            assert "TRON: Legacy (2010)" in result
            assert "Breaking Bad" not in result  # Should not appear (rating 8)
            # Verify API endpoint includes rating filter
            call_args = mock_http_client.get.call_args
            assert "/sync/ratings/movies/10" in call_args[0][0]
            assert call_args[1]["params"]["page"] == 1


@pytest.mark.asyncio
async def test_fetch_user_ratings_paginated_empty_result_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test paginated user ratings with empty results through complete stack."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        # Mock empty paginated response
        empty_mock = MagicMock()
        empty_mock.json.return_value = []
        empty_mock.raise_for_status = MagicMock()
        # Mock pagination headers for empty results
        empty_mock.headers = {
            "X-Pagination-Page": "1",
            "X-Pagination-Limit": "10",
            "X-Pagination-Page-Count": "1",
            "X-Pagination-Item-Count": "0",
        }

        mock_http_client.get.return_value = empty_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="seasons", page=1)
            # Verify empty paginated state handling
            assert "# Your Seasons Ratings" in result
            assert "You haven't rated any seasons yet" in result
            assert "📄 **Pagination Info:** 0 total items" in result

            # Verify page parameter was sent
            call_args = mock_http_client.get.call_args
            assert call_args[1]["params"]["page"] == 1


@pytest.mark.asyncio
async def test_fetch_user_ratings_backward_compatibility_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test that non-paginated requests still work alongside paginated ones."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        # Mock non-paginated response (no pagination headers)
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = SAMPLE_USER_RATINGS_RESPONSE
        ratings_mock.raise_for_status = MagicMock()
        mock_http_client.get.return_value = ratings_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            # Test without page parameter (non-paginated request)
            result = await fetch_user_ratings(rating_type="movies")
            # Verify response format (pagination info is always present in response structure)
            assert "# Your Movies Ratings" in result
            assert "Found 3 rated movies on this page" in result
            assert "TRON: Legacy (2010)" in result
            # Response will contain pagination metadata (with default values when no headers present)
            assert "📄" in result

            # Verify NO pagination parameters were sent (following "Pagination Optional" pattern)
            call_args = mock_http_client.get.call_args
            call_kwargs = call_args[1]
            assert "params" not in call_kwargs or not call_kwargs["params"]


@pytest.mark.asyncio
async def test_fetch_user_ratings_pagination_error_handling_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test pagination error handling through complete stack."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        # Mock HTTP error during paginated request
        mock_http_client.get.side_effect = Exception("Pagination API error")

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings
            from utils.api.errors import InternalError

            # Should handle pagination errors gracefully
            with pytest.raises(InternalError) as exc_info:
                await fetch_user_ratings(rating_type="movies", page=1)

            assert "unexpected error occurred" in str(exc_info.value).lower()
            # Verify page parameter was attempted
            call_args = mock_http_client.get.call_args
            assert call_args[1]["params"]["page"] == 1


@pytest.mark.asyncio
async def test_fetch_user_ratings_pagination_authentication_flow_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test that paginated requests require authentication just like regular requests."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create unauthenticated sync client
        sync_client = SyncClient()
        sync_client.is_authenticated = lambda: False

        with patch("server.sync.tools.SyncClient", return_value=sync_client):
            from server.sync.tools import fetch_user_ratings

            # Paginated request should also require authentication
            with pytest.raises(
                ValueError,
                match="You must be authenticated to access your personal ratings",
            ):
                await fetch_user_ratings(rating_type="movies", page=1)


@pytest.mark.asyncio
async def test_fetch_user_ratings_pagination_headers_extraction_integration(
    authenticated_sync_client: SyncClient,
) -> None:
    """Test that pagination headers are correctly extracted and processed."""

    with patch.dict(
        os.environ,
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    ):
        # Create mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.aclose = AsyncMock()
        mock_http_client.get = AsyncMock()
        # Mock response with specific pagination headers
        ratings_mock = MagicMock()
        ratings_mock.json.return_value = SAMPLE_USER_RATINGS_RESPONSE[:1]
        ratings_mock.raise_for_status = MagicMock()
        # Mock specific pagination header values for testing
        ratings_mock.headers = {
            "X-Pagination-Page": "3",
            "X-Pagination-Limit": "5",
            "X-Pagination-Page-Count": "10",
            "X-Pagination-Item-Count": "47",
        }

        mock_http_client.get.return_value = ratings_mock

        with (
            patch.object(
                authenticated_sync_client, "_get_client", return_value=mock_http_client
            ),
            patch(
                "server.sync.tools.SyncClient", return_value=authenticated_sync_client
            ),
        ):
            from server.sync.tools import fetch_user_ratings

            result = await fetch_user_ratings(rating_type="shows", page=3)
            # Verify pagination metadata is correctly extracted and formatted
            assert "📄 **Page 3 of 10" in result
            assert "items 11-11 of 47" in result  # Calculated based on page 3, limit 5
            assert "📍 **Navigation:** Previous: page 2 | Next: page 4" in result
            assert "Found 1 rated show on this page" in result

            # Verify correct API call
            call_args = mock_http_client.get.call_args
            assert call_args[1]["params"]["page"] == 3
