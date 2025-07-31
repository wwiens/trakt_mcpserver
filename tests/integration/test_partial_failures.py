"""Integration tests for partial failure scenarios."""

from typing import Any
from unittest.mock import patch

import pytest

from client.movies.client import MoviesClient
from client.search.client import SearchClient
from client.shows.client import ShowsClient
from client.user.client import UserClient
from config.errors import AUTH_REQUIRED
from server.movies.tools import fetch_movie_summary
from server.search.tools import search_shows
from server.shows.tools import fetch_show_summary
from server.user.tools import fetch_user_watched_shows
from utils.api.errors import InvalidRequestError


class TestPartialFailures:
    """Test partial failure scenarios in batch-like operations."""

    @pytest.mark.asyncio
    async def test_search_with_mixed_results(self):
        """Test search returning mix of valid and invalid results."""
        # Mock search results with some valid, some problematic data (raw API format)
        mixed_search_results = [
            {
                "type": "show",
                "score": 95.0,
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "ids": {
                        "trakt": 1,
                        "slug": "breaking-bad",
                        "imdb": "tt0903747",
                        "tmdb": 1396,
                    },
                },
            },
            {
                "type": "show",
                "score": 85.0,
                "show": {
                    "title": "Show With Missing Data",
                    "year": None,  # Missing year
                    "ids": {"trakt": 2, "slug": "missing-data-show"},
                    # Missing some IDs
                },
            },
            {
                "type": "show",
                "score": 75.0,
                "show": {
                    "title": "Another Valid Show",
                    "year": 2020,
                    "ids": {
                        "trakt": 3,
                        "slug": "valid-show",
                        "imdb": "tt1234567",
                        "tmdb": 5678,
                    },
                },
            },
        ]

        with patch.object(
            SearchClient, "search_shows", return_value=mixed_search_results
        ):
            result = await search_shows("test query", limit=10)

            # Should return formatted results for all shows, even with missing data
            assert "Breaking Bad" in result
            assert "Show With Missing Data" in result
            assert "Another Valid Show" in result
            assert "2008" in result  # Breaking Bad year
            assert "2020" in result  # Another Valid Show year
            # Missing year should be handled gracefully (None or blank)

    @pytest.mark.asyncio
    async def test_user_data_partial_access(self):
        """Test user data where some information is accessible, some isn't."""
        # Mock scenario where user has some shows but API returns partial data
        partial_shows_data: list[dict[str, Any]] = [
            {
                "last_watched_at": "2023-01-15T20:30:00Z",
                "last_updated_at": "2023-01-15T20:30:00Z",
                "plays": 25,
                "reset_at": None,
                "seasons": [
                    {
                        "number": 1,
                        "episodes": [
                            {
                                "number": 1,
                                "plays": 3,
                                "last_watched_at": "2023-01-10T19:00:00Z",
                            },
                            {
                                "number": 2,
                                "plays": 2,
                                "last_watched_at": "2023-01-12T20:00:00Z",
                            },
                        ],
                    }
                ],
                "show": {
                    "title": "Complete Show Data",
                    "year": 2020,
                    "ids": {
                        "trakt": 1,
                        "slug": "complete-show",
                        "imdb": "tt1111111",
                        "tmdb": 1111,
                    },
                },
            },
            {
                "last_watched_at": "2023-02-01T21:00:00Z",
                "last_updated_at": "2023-02-01T21:00:00Z",
                "plays": 10,
                "reset_at": None,
                "seasons": [],  # Empty seasons data
                "show": {
                    "title": "Show With Missing Season Data",
                    "year": 2021,
                    "ids": {"trakt": 2, "slug": "missing-seasons"},
                    # Missing some IDs
                },
            },
        ]

        with (
            patch.object(
                UserClient, "get_user_watched_shows", return_value=partial_shows_data
            ),
            patch.object(UserClient, "is_authenticated", return_value=True),
        ):
            # Should be authenticated for this to work
            result = await fetch_user_watched_shows()

            # Should format both shows despite partial data
            assert "Complete Show Data" in result
            assert "Show With Missing Season Data" in result
            assert "25" in result  # Complete show plays
            assert "10" in result  # Partial show plays
            # Missing season data should be handled gracefully

    @pytest.mark.asyncio
    async def test_movie_details_with_missing_fields(self):
        """Test movie details where some fields are missing."""
        # Mock movie with partial data (raw API format)
        partial_movie = {
            "title": "Partial Movie Data",
            "year": 2022,
            "ids": {"trakt": 123, "slug": "partial-movie"},
            # Missing many optional fields like runtime, genres, etc.
            "tagline": None,
            "overview": "A movie with minimal data available.",
            "released": None,
            "runtime": None,
            "country": None,
            "trailer": None,
            "homepage": None,
            "status": None,
            "rating": None,
            "votes": None,
            "comment_count": None,
            "language": None,
            "genres": None,
            "certification": None,
        }

        with patch.object(MoviesClient, "_make_request", return_value=partial_movie):
            result = await fetch_movie_summary("123")

            # Should handle missing fields gracefully
            assert "Partial Movie Data" in result
            assert "2022" in result
            assert "A movie with minimal data available." in result
            # Missing fields should not cause errors

    @pytest.mark.asyncio
    async def test_show_with_incomplete_statistics(self):
        """Test show with partial/missing statistical data."""
        # Mock show with basic data but missing extended info (raw API format)
        basic_show = {
            "title": "Basic Show Info",
            "year": 2023,
            "ids": {"trakt": 456, "slug": "basic-show", "imdb": "tt2222222"},
            # Missing many optional fields
            "overview": None,
            "first_aired": None,
            "airs": None,
            "runtime": None,
            "certification": None,
            "network": None,
            "country": None,
            "trailer": None,
            "homepage": None,
            "status": None,
            "rating": None,
            "votes": None,
            "comment_count": None,
            "language": None,
            "genres": None,
            "aired_episodes": None,
        }

        with patch.object(ShowsClient, "_make_request", return_value=basic_show):
            result = await fetch_show_summary("basic-show")

            # Should work with minimal data
            assert "Basic Show Info" in result
            assert "2023" in result
            # Missing statistical data should be handled gracefully

    @pytest.mark.asyncio
    async def test_api_response_with_null_values(self):
        """Test handling of API responses containing null/None values."""
        # Simulate API returning data with explicit null values
        api_response_with_nulls: dict[str, Any] = {
            "title": "Show With Nulls",
            "year": 2023,
            "ids": {
                "trakt": 789,
                "slug": "show-with-nulls",
                "imdb": None,
                "tmdb": None,
            },
            "overview": None,
            "first_aired": None,
            "runtime": None,
            "rating": None,
            "votes": 0,  # Zero votes is valid
            "genres": [],  # Empty array is valid
            "language": "",  # Empty string
            "network": None,
            "status": None,
        }

        # Mock the client to return this data structure
        with patch.object(
            ShowsClient, "_make_request", return_value=api_response_with_nulls
        ):
            result = await fetch_show_summary("show-with-nulls")

            # Should handle null values gracefully
            assert "Show With Nulls" in result
            assert "2023" in result

    @pytest.mark.asyncio
    async def test_mixed_error_and_success_responses(self):
        """Test scenarios with mixed successful and error responses."""
        # This simulates a case where the API call fails with a rate limit error
        call_count = 0

        def mock_api_call(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call fails
                raise InvalidRequestError(
                    "Temporary error",
                    data={"http_status": 429},  # Rate limit
                )
            else:
                # Second call succeeds (in real scenarios, this would be a retry)
                return {
                    "title": "Eventually Successful Movie",
                    "year": 2023,
                    "ids": {"trakt": 999, "slug": "eventual-success"},
                    "overview": "This worked after initial failure.",
                }

        # Test that single API failures propagate correctly
        with patch.object(MoviesClient, "_make_request", side_effect=mock_api_call):
            # First call should fail with rate limit error
            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_movie_summary("123")

            assert exc_info.value.code == -32600
            assert "Temporary error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_large_dataset_with_some_invalid_entries(self):
        """Test processing large datasets where some entries are invalid."""
        # Create a large search result set with some problematic entries
        large_mixed_results: list[dict[str, Any]] = []

        for i in range(20):
            if i % 7 == 0:  # Every 7th entry has issues
                # Problematic entry (raw API format)
                large_mixed_results.append(
                    {
                        "type": "show",
                        "score": 50.0,
                        "show": {
                            "title": f"Problematic Show {i}",
                            "year": None,  # Missing year
                            "ids": {"trakt": i, "slug": f"problem-{i}"},
                            # Missing other IDs
                        },
                    }
                )
            else:
                # Normal entry (raw API format)
                large_mixed_results.append(
                    {
                        "type": "show",
                        "score": 90.0,
                        "show": {
                            "title": f"Normal Show {i}",
                            "year": 2020 + (i % 5),
                            "ids": {
                                "trakt": i,
                                "slug": f"normal-{i}",
                                "imdb": f"tt{i:07d}",
                                "tmdb": i * 100,
                            },
                        },
                    }
                )

        with patch.object(
            SearchClient, "_make_request", return_value=large_mixed_results
        ):
            result = await search_shows("large dataset test", limit=30)

            # Should process all entries, even problematic ones
            assert "Normal Show 1" in result
            assert "Normal Show 8" in result
            assert "Problematic Show 0" in result
            assert "Problematic Show 14" in result

            # Should have proper formatting for all entries
            assert "2020" in result  # Some years should be present
            assert "2024" in result  # Range of years

            # Count the number of shows mentioned (should be 20)
            # Each show appears as "**1. Title**", "**2. Title**", etc.
            show_count = result.count("**")
            assert show_count >= 40  # At least 20 shows with 2 ** each

    @pytest.mark.asyncio
    async def test_authentication_state_changes_during_operation(self):
        """Test operations where auth state might change mid-operation."""
        auth_state = True

        def mock_is_authenticated():
            return auth_state

        def mock_api_call(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
            nonlocal auth_state
            if auth_state:
                # First call works, but then auth expires
                auth_state = False
                return [
                    {
                        "some": "data",
                        "show": {
                            "title": "Test Show",
                            "year": 2023,
                            "ids": {"trakt": 1},
                        },
                    }
                ]
            else:
                # Subsequent calls fail due to auth expiry
                raise InvalidRequestError(
                    AUTH_REQUIRED,
                    data={"http_status": 401},
                )

        with (
            patch.object(
                UserClient, "is_authenticated", side_effect=mock_is_authenticated
            ),
            patch.object(
                UserClient, "get_user_watched_shows", side_effect=mock_api_call
            ),
        ):
            # First call should succeed
            result = await fetch_user_watched_shows()
            assert "Test Show" in result

            # Second call should fail with auth error (no auth token available)
            with patch(
                "server.user.tools.start_device_auth", return_value="Auth required"
            ):
                result2 = await fetch_user_watched_shows()
                assert "Auth required" in result2
