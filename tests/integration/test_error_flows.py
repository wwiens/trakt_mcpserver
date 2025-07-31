"""Integration tests for error flow scenarios."""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.errors import AUTH_REQUIRED
from utils.api.errors import InternalError, InvalidParamsError, InvalidRequestError


class TestErrorFlowIntegration:
    """Integration tests for end-to-end error flows."""

    @pytest.mark.asyncio
    async def test_401_error_flow_movies(self):
        """Test 401 error flow from HTTP response → client → server → MCP error."""
        from server.movies.tools import fetch_movie_ratings

        with patch("server.movies.tools.MoviesClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Simulate the actual error flow: HTTP 401 → @handle_api_errors → InvalidRequestError
            mock_client.get_movie.side_effect = InvalidRequestError(
                AUTH_REQUIRED,
                data={"http_status": 401},
            )

            # The MCP error should propagate all the way through
            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_movie_ratings(movie_id="123")

            # Verify the complete error flow
            assert exc_info.value.code == -32600
            assert "Authentication required" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 401

    @pytest.mark.asyncio
    async def test_404_error_flow_shows(self):
        """Test 404 error flow from HTTP response → client → server → MCP error."""
        from server.shows.tools import fetch_show_summary

        with patch("server.shows.tools.ShowsClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Simulate the actual error flow: HTTP 404 → @handle_api_errors → InvalidRequestError
            mock_client.get_show_extended.side_effect = InvalidRequestError(
                "The requested resource was not found.", data={"http_status": 404}
            )

            # The MCP error should propagate all the way through
            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_show_summary(show_id="nonexistent")

            # Verify the complete error flow
            assert exc_info.value.code == -32600
            assert "not found" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 404

    @pytest.mark.asyncio
    async def test_429_error_flow_search(self):
        """Test 429 error flow from HTTP response → client → server → MCP error."""
        from server.search.tools import search_movies

        with patch("server.search.tools.SearchClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Simulate the actual error flow: HTTP 429 → @handle_api_errors → InvalidRequestError
            mock_client.search_movies.side_effect = InvalidRequestError(
                "Rate limit exceeded. Please try again later.",
                data={"http_status": 429},
            )

            # The MCP error should propagate all the way through
            with pytest.raises(InvalidRequestError) as exc_info:
                await search_movies(query="test", limit=10)

            # Verify the complete error flow
            assert exc_info.value.code == -32600
            assert "Rate limit exceeded" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 429

    @pytest.mark.asyncio
    async def test_500_error_flow_comments(self):
        """Test 500 error flow from HTTP response → client → server → MCP error."""
        from server.comments.tools import fetch_movie_comments

        with patch("server.comments.tools.CommentsClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Simulate the actual error flow: HTTP 500 → @handle_api_errors → InternalError
            mock_client.get_movie_comments.side_effect = InternalError(
                "HTTP 500 error occurred",
                data={"http_status": 500, "response": "Internal Server Error"},
            )

            # The MCP error should propagate all the way through
            with pytest.raises(InternalError) as exc_info:
                await fetch_movie_comments(movie_id="123")

            # Verify the complete error flow
            assert exc_info.value.code == -32603
            assert "HTTP 500 error occurred" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 500

    @pytest.mark.asyncio
    async def test_network_error_flow_checkin(self):
        """Test network error flow from connection failure → client → server → MCP error."""
        from server.checkin.tools import checkin_to_show

        with patch("server.checkin.tools.CheckinClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Simulate the actual error flow: Network failure → @handle_api_errors → InternalError
            mock_client.is_authenticated.return_value = True
            mock_client.checkin_to_show.side_effect = InternalError(
                "Unable to connect to Trakt API. Please check your internet connection.",
                data={"error_type": "request_error", "details": "Connection failed"},
            )

            # The MCP error should propagate all the way through
            with pytest.raises(InternalError) as exc_info:
                await checkin_to_show(season=1, episode=1, show_id="123")

            # Verify the complete error flow
            assert exc_info.value.code == -32603
            assert "Unable to connect" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["error_type"] == "request_error"

    @pytest.mark.asyncio
    async def test_multiple_api_calls_with_errors(self):
        """Test error handling when multiple API calls are made and one fails."""
        from server.movies.tools import fetch_movie_ratings

        with patch("server.movies.tools.MoviesClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # First call succeeds
            async def async_return_movie():
                return {"title": "Test Movie", "year": 2023}

            mock_client.get_movie.return_value = async_return_movie()

            # Second call fails with MCP error
            mock_client.get_movie_ratings.side_effect = InvalidRequestError(
                "Access forbidden. You don't have permission to access this resource.",
                data={"http_status": 403},
            )

            # The error from the second call should propagate
            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_movie_ratings(movie_id="123")

            # Verify both calls were made
            mock_client.get_movie.assert_called_once_with("123")
            mock_client.get_movie_ratings.assert_called_once_with("123")

            # Verify the error from the second call
            assert exc_info.value.code == -32600
            assert "Access forbidden" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 403

    @pytest.mark.asyncio
    async def test_authentication_pre_check_flow(self):
        """Test the authentication pre-check flow in user tools."""
        from server.user.tools import fetch_user_watched_shows

        with (
            patch("server.user.tools.UserClient") as mock_client_class,
            patch("server.user.tools.start_device_auth") as mock_start_auth,
        ):
            mock_client = mock_client_class.return_value

            # Mock get_user_watched_shows to raise InvalidParamsError (not authenticated)
            mock_client.get_user_watched_shows.side_effect = InvalidParamsError(AUTH_REQUIRED)

            # Mock the auth start function
            mock_start_auth.return_value = "Please visit https://trakt.tv/activate..."

            # This should return auth instructions, not raise an exception
            result = await fetch_user_watched_shows(limit=10)

            # Verify it returns authentication instructions
            assert isinstance(result, str)
            assert "Authentication required" in result or "Please visit" in result

            # Verify the method was called and triggered the exception
            mock_client.get_user_watched_shows.assert_called_once()
            mock_start_auth.assert_called_once()

    @pytest.mark.asyncio
    async def test_correct_client_server_error_flow(self):
        """Test that client exceptions properly propagate through server tools."""
        from server.shows.tools import fetch_show_ratings

        # Test: Client raises MCP exception, server tool should let it propagate
        with patch("server.shows.tools.ShowsClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            async def async_raise_error(*args: Any, **kwargs: Any) -> None:
                raise InvalidRequestError("Show not found", -32600)

            mock_client.get_show.side_effect = async_raise_error

            # Server tool should let the MCP exception propagate
            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_show_ratings(show_id="123")

            assert exc_info.value.code == -32600
            assert "Show not found" in str(exc_info.value)


class TestEdgeCaseErrorHandling:
    """Test edge cases and corner scenarios for error handling."""

    @pytest.mark.asyncio
    async def test_concurrent_errors(self):
        """Test error handling when multiple operations fail concurrently."""
        from server.movies.tools import fetch_trending_movies
        from server.shows.tools import fetch_trending_shows

        # Both operations should fail with different errors
        with (
            patch("server.movies.tools.MoviesClient") as mock_movies_client,
            patch("server.shows.tools.ShowsClient") as mock_shows_client,
        ):
            mock_movies_client.return_value.get_trending_movies.side_effect = (
                InvalidRequestError(
                    AUTH_REQUIRED,
                    data={"http_status": 401},
                )
            )

            mock_shows_client.return_value.get_trending_shows.side_effect = (
                InvalidRequestError(
                    "Rate limit exceeded. Please try again later.",
                    data={"http_status": 429},
                )
            )

            # Run both concurrently and catch their errors
            with pytest.raises(InvalidRequestError) as movies_exc:
                await fetch_trending_movies(limit=5)

            with pytest.raises(InvalidRequestError) as shows_exc:
                await fetch_trending_shows(limit=5)

            # Each should have their specific error
            assert "Authentication required" in movies_exc.value.message
            assert movies_exc.value.data is not None
            assert movies_exc.value.data["http_status"] == 401

            assert "Rate limit exceeded" in shows_exc.value.message
            assert shows_exc.value.data is not None
            assert shows_exc.value.data["http_status"] == 429

    @pytest.mark.asyncio
    async def test_error_data_preservation(self):
        """Test that error data is preserved through propagation."""
        from server.comments.tools import fetch_comment

        with patch("server.comments.tools.CommentsClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Create error with rich data
            original_error = InvalidRequestError(
                "The requested resource was not found.",
                data={
                    "http_status": 404,
                    "request_id": "req_123456",
                    "endpoint": "/comments/987654",
                    "timestamp": "2023-01-01T00:00:00Z",
                    "user_context": {"user_id": "user_789"},
                },
            )

            mock_client.get_comment.side_effect = original_error

            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_comment(comment_id="987654")

            # All original data should be preserved
            propagated_error = exc_info.value
            assert propagated_error.data is not None
            assert propagated_error.data["http_status"] == 404
            assert propagated_error.data is not None
            assert propagated_error.data["request_id"] == "req_123456"
            assert propagated_error.data is not None
            assert propagated_error.data["endpoint"] == "/comments/987654"
            assert propagated_error.data is not None
            assert propagated_error.data["timestamp"] == "2023-01-01T00:00:00Z"
            assert propagated_error.data is not None
            assert propagated_error.data["user_context"]["user_id"] == "user_789"

    @pytest.mark.asyncio
    async def test_nested_error_contexts(self):
        """Test error handling in nested function calls."""
        from server.comments.tools import fetch_comment_replies

        with patch("server.comments.tools.CommentsClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Mock the first call to succeed and second call to fail
            async def async_return_comment():
                return {
                    "id": "123",
                    "comment": "Test comment",
                    "user": {"username": "testuser"},
                }

            mock_client.get_comment.return_value = async_return_comment()

            # Simulate error in nested context
            mock_client.get_comment_replies.side_effect = InternalError(
                "HTTP 503 error occurred",
                data={
                    "http_status": 503,
                    "response": "Service Unavailable",
                    "retry_after": 60,
                    "service": "comments",
                    "call_stack": [
                        "get_comment_replies",
                        "fetch_from_api",
                        "http_client",
                    ],
                },
            )

            with pytest.raises(InternalError) as exc_info:
                await fetch_comment_replies(comment_id="123")

            # Nested context data should be preserved
            assert exc_info.value.code == -32603
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 503
            assert exc_info.value.data is not None
            assert exc_info.value.data["retry_after"] == 60
            assert exc_info.value.data is not None
            assert exc_info.value.data["service"] == "comments"
            assert exc_info.value.data is not None
            assert "call_stack" in exc_info.value.data
