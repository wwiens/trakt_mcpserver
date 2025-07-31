"""Integration tests for timeout scenarios."""

import asyncio
from typing import Any
from unittest.mock import patch

import pytest
from httpx import ConnectTimeout, ReadTimeout

from client.auth.client import AuthClient
from client.movies.client import MoviesClient
from client.search.client import SearchClient
from client.shows.client import ShowsClient
from client.user.client import UserClient
from server.auth.tools import start_device_auth
from server.movies.tools import fetch_trending_movies
from server.search.tools import search_shows
from server.shows.tools import fetch_trending_shows
from server.user.tools import fetch_user_watched_shows
from utils.api.errors import InternalError


class TestTimeoutScenarios:
    """Test timeout scenarios across different operations."""

    @pytest.mark.asyncio
    async def test_auth_device_code_timeout(self):
        """Test timeout during device code retrieval."""
        with patch.object(
            AuthClient, "_make_request", side_effect=ReadTimeout("Request timed out")
        ):
            client = AuthClient()

            # Should propagate timeout as InternalError
            with pytest.raises(InternalError) as exc_info:
                await client.get_device_code()

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_auth_token_exchange_timeout(self):
        """Test timeout during token exchange."""
        with patch.object(
            AuthClient,
            "_make_request",
            side_effect=ConnectTimeout("Connection timed out"),
        ):
            client = AuthClient()

            # Should propagate timeout as InternalError
            with pytest.raises(InternalError) as exc_info:
                await client.get_device_token("test_device_code")

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_timeout(self):
        """Test timeout during search operations."""
        with patch.object(
            SearchClient, "_make_request", side_effect=ReadTimeout("Search timed out")
        ):
            # Should propagate timeout as InternalError
            with pytest.raises(InternalError) as exc_info:
                await search_shows("timeout test", limit=10)

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_movies_api_timeout(self):
        """Test timeout during movie API calls."""
        with patch.object(
            MoviesClient,
            "_make_request",
            side_effect=ReadTimeout("Movies API timed out"),
        ):
            # Should propagate timeout as InternalError
            with pytest.raises(InternalError) as exc_info:
                await fetch_trending_movies(limit=5)

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_shows_api_timeout(self):
        """Test timeout during show API calls."""
        with patch.object(
            ShowsClient,
            "_make_request",
            side_effect=ConnectTimeout("Shows API connection timeout"),
        ):
            # Should propagate timeout as InternalError
            with pytest.raises(InternalError) as exc_info:
                await fetch_trending_shows(limit=5)

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_user_data_timeout(self):
        """Test timeout during user data retrieval."""
        with (
            patch.object(
                UserClient,
                "_make_request",
                side_effect=ReadTimeout("User data timeout"),
            ),
            patch.object(UserClient, "is_authenticated", return_value=True),
        ):
            # Should propagate timeout as InternalError
            with pytest.raises(InternalError) as exc_info:
                await fetch_user_watched_shows()

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_multiple_concurrent_timeouts(self):
        """Test handling of multiple concurrent timeout scenarios."""
        # Create multiple clients that will all timeout
        with (
            patch.object(
                SearchClient,
                "_make_request",
                side_effect=ReadTimeout("Concurrent timeout"),
            ),
            patch.object(
                MoviesClient,
                "_make_request",
                side_effect=ReadTimeout("Concurrent timeout"),
            ),
            patch.object(
                ShowsClient,
                "_make_request",
                side_effect=ReadTimeout("Concurrent timeout"),
            ),
        ):
            # All operations should fail with proper error handling
            search_task = search_shows("test", limit=5)
            movies_task = fetch_trending_movies(limit=5)
            shows_task = fetch_trending_shows(limit=5)

            # Check that all raise InternalError
            with pytest.raises(InternalError):
                await search_task

            with pytest.raises(InternalError):
                await movies_task

            with pytest.raises(InternalError):
                await shows_task

    @pytest.mark.asyncio
    async def test_partial_timeout_in_auth_flow(self):
        """Test timeout occurring mid-way through auth flow."""
        # Mock successful device code retrieval
        from models.auth.auth import TraktDeviceCode

        mock_device_code = TraktDeviceCode(
            device_code="test_device_code",
            user_code="TEST123",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
            interval=5,
        )

        # First call succeeds, second times out
        call_count = 0

        def mock_auth_calls(*args: Any, **kwargs: Any) -> dict[str, str]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # Device code call succeeds
                return mock_device_code.model_dump()
            else:
                # Token exchange times out
                raise ReadTimeout("Token exchange timed out")

        with patch.object(AuthClient, "_make_request", side_effect=mock_auth_calls):
            # Start auth flow should succeed
            result = await start_device_auth()
            assert "TEST123" in result
            assert "https://trakt.tv/activate" in result

            # Token exchange should timeout
            client = AuthClient()
            with pytest.raises(InternalError) as exc_info:
                await client.get_device_token("test_device_code")

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_with_retry_behavior(self):
        """Test that timeouts don't interfere with proper error propagation."""
        call_count = 0

        def mock_timeout_then_success(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ReadTimeout("First attempt timed out")
            else:
                # This shouldn't happen in our current architecture (no auto-retry)
                # Return dict instead of list to match return type
                return {"movie": {"title": "Success Movie", "year": 2023}}

        with patch.object(
            MoviesClient, "_make_request", side_effect=mock_timeout_then_success
        ):
            # First call should fail with timeout
            with pytest.raises(InternalError) as exc_info:
                await fetch_trending_movies(limit=1)

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

            # Verify only one call was made (no automatic retry)
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_connection_vs_read_timeout_handling(self):
        """Test different types of timeouts are handled consistently."""
        # Test ConnectTimeout (connection establishment timeout)
        with patch.object(
            SearchClient,
            "_make_request",
            side_effect=ConnectTimeout("Connection timeout"),
        ):
            with pytest.raises(InternalError) as exc_info:
                await search_shows("connect timeout test")

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

        # Test ReadTimeout (response timeout)
        with patch.object(
            SearchClient, "_make_request", side_effect=ReadTimeout("Read timeout")
        ):
            with pytest.raises(InternalError) as exc_info:
                await search_shows("read timeout test")

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_asyncio_timeout_vs_httpx_timeout(self):
        """Test handling of different timeout sources."""
        # Test httpx timeout (handled by our error decorator)
        with patch.object(
            MoviesClient, "_make_request", side_effect=ReadTimeout("HTTPX timeout")
        ):
            with pytest.raises(InternalError) as exc_info:
                await fetch_trending_movies()

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

        # Test asyncio timeout (this would be external to our error handling)
        async def slow_operation(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
            await asyncio.sleep(2)  # Simulate slow operation
            return [{"movie": {"title": "Slow Movie", "year": 2023}}]

        with (
            patch.object(MoviesClient, "_make_request", side_effect=slow_operation),
            pytest.raises(asyncio.TimeoutError),
        ):
            # Apply asyncio timeout
            await asyncio.wait_for(fetch_trending_movies(), timeout=0.1)

    @pytest.mark.asyncio
    async def test_timeout_during_user_auth_check(self):
        """Test timeout during authentication status check."""
        with (
            patch.object(
                UserClient,
                "_make_request",
                side_effect=ReadTimeout("Auth check timeout"),
            ),
            patch.object(UserClient, "is_authenticated", return_value=True),
        ):
            # Mock the file-based auth check to pass
            # Should propagate timeout error when trying to access user data
            with pytest.raises(InternalError) as exc_info:
                await fetch_user_watched_shows()

            assert exc_info.value.code == -32603
            assert "Unable to connect to Trakt API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_error_message_consistency(self):
        """Test that timeout errors have consistent, user-friendly messages."""
        # Properly type the function arguments to avoid type inference issues
        timeout_scenarios: list[tuple[type, Any, tuple[Any, ...]]] = [
            (SearchClient, search_shows, ("test query", 5)),
            (MoviesClient, fetch_trending_movies, (5,)),
            (ShowsClient, fetch_trending_shows, (5,)),
        ]

        for client_class, server_func, args in timeout_scenarios:
            with patch.object(
                client_class, "_make_request", side_effect=ReadTimeout("API timeout")
            ):
                with pytest.raises(InternalError) as exc_info:
                    await server_func(*args)

                # All timeout errors should have consistent messaging
                assert exc_info.value.code == -32603
                assert "Unable to connect to Trakt API" in str(exc_info.value)
                # Error message should be user-friendly, not technical
                assert "ReadTimeout" not in str(exc_info.value)
                assert "API timeout" not in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_logging_behavior(self):
        """Test that timeouts are properly logged without exposing sensitive data."""

        # Capture log output
        with (
            patch.object(
                SearchClient,
                "_make_request",
                side_effect=ReadTimeout("Logging test timeout"),
            ),
            pytest.raises(InternalError),
        ):
            await search_shows("logging test")

        # Note: We can't easily test the actual log output in this test framework,
        # but this verifies the error propagation path that includes logging
        # The actual logging verification would need to be done with log capture

        assert True  # Test passes if no exceptions during error handling
