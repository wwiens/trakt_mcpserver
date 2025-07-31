"""Tests for MCP compliance and error code consistency."""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from config.errors import AUTH_REQUIRED
from utils.api.errors import InternalError, InvalidRequestError


class TestMCPErrorCodeCompliance:
    """Test MCP error codes are returned correctly according to JSON-RPC 2.0 spec."""

    @pytest.mark.asyncio
    async def test_401_authentication_error_returns_invalid_request(self):
        """Test that 401 authentication errors return InvalidRequestError (-32600)."""
        from server.movies.tools import fetch_movie_ratings

        with patch("server.movies.tools.MoviesClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_movie.side_effect = InvalidRequestError(
                AUTH_REQUIRED,
                data={"http_status": 401},
            )

            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_movie_ratings(movie_id="123")

            # Verify it's the correct MCP error code
            assert exc_info.value.code == -32600  # Invalid Request
            assert "Authentication required" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 401

    @pytest.mark.asyncio
    async def test_404_not_found_error_returns_invalid_request(self):
        """Test that 404 not found errors return InvalidRequestError (-32600)."""
        from server.shows.tools import fetch_show_summary

        with patch("server.shows.tools.ShowsClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_show_extended.side_effect = InvalidRequestError(
                "The requested resource was not found.", data={"http_status": 404}
            )

            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_show_summary(show_id="nonexistent")

            # Verify it's the correct MCP error code
            assert exc_info.value.code == -32600  # Invalid Request
            assert "not found" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 404

    @pytest.mark.asyncio
    async def test_429_rate_limit_error_returns_invalid_request(self):
        """Test that 429 rate limit errors return InvalidRequestError (-32600)."""
        from server.search.tools import search_shows

        with patch("server.search.tools.SearchClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.search_shows.side_effect = InvalidRequestError(
                "Rate limit exceeded. Please try again later.",
                data={"http_status": 429},
            )

            with pytest.raises(InvalidRequestError) as exc_info:
                await search_shows(query="test")

            # Verify it's the correct MCP error code
            assert exc_info.value.code == -32600  # Invalid Request
            assert "Rate limit exceeded" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 429

    @pytest.mark.asyncio
    async def test_500_server_error_returns_internal_error(self):
        """Test that 500 server errors return InternalError (-32603)."""
        from server.movies.tools import fetch_trending_movies

        with patch("server.movies.tools.MoviesClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_trending_movies.side_effect = InternalError(
                "HTTP 500 error occurred",
                data={"http_status": 500, "response": "Internal Server Error"},
            )

            with pytest.raises(InternalError) as exc_info:
                await fetch_trending_movies(limit=10)

            # Verify it's the correct MCP error code
            assert exc_info.value.code == -32603  # Internal Error
            assert "HTTP 500 error occurred" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 500

    @pytest.mark.asyncio
    async def test_network_error_returns_internal_error(self):
        """Test that network connection errors return InternalError (-32603)."""
        from server.shows.tools import fetch_popular_shows

        with patch("server.shows.tools.ShowsClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_popular_shows.side_effect = InternalError(
                "Unable to connect to Trakt API. Please check your internet connection.",
                data={"error_type": "request_error", "details": "Connection failed"},
            )

            with pytest.raises(InternalError) as exc_info:
                await fetch_popular_shows(limit=5)

            # Verify it's the correct MCP error code
            assert exc_info.value.code == -32603  # Internal Error
            assert "Unable to connect to Trakt API" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["error_type"] == "request_error"

    @pytest.mark.asyncio
    async def test_client_error_status_codes_map_to_invalid_request(self):
        """Test that all 4xx client errors map to InvalidRequestError (-32600)."""
        from server.comments.tools import fetch_movie_comments

        client_error_codes = [400, 403, 422]
        error_messages = [
            "Bad request. Please check your request parameters.",
            "Access forbidden. You don't have permission to access this resource.",
            "Unprocessable entity. The request is syntactically correct but semantically invalid.",
        ]

        for status_code, expected_message in zip(
            client_error_codes, error_messages, strict=False
        ):
            with patch("server.comments.tools.CommentsClient") as mock_client_class:
                mock_client = mock_client_class.return_value
                mock_client.get_movie_comments.side_effect = InvalidRequestError(
                    expected_message, data={"http_status": status_code}
                )

                with pytest.raises(InvalidRequestError) as exc_info:
                    await fetch_movie_comments(movie_id="123")

                # Verify it's the correct MCP error code
                assert exc_info.value.code == -32600  # Invalid Request
                assert exc_info.value.data is not None
                assert exc_info.value.data["http_status"] == status_code

    @pytest.mark.asyncio
    async def test_unknown_http_error_returns_internal_error(self):
        """Test that unknown HTTP errors (like 503) return InternalError (-32603)."""
        from server.checkin.tools import checkin_to_show

        with patch("server.checkin.tools.CheckinClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.is_authenticated.return_value = True
            mock_client.checkin_to_show.side_effect = InternalError(
                "HTTP 503 error occurred",
                data={"http_status": 503, "response": "Service Unavailable"},
            )

            with pytest.raises(InternalError) as exc_info:
                await checkin_to_show(season=1, episode=1, show_id="123")

            # Verify it's the correct MCP error code
            assert exc_info.value.code == -32603  # Internal Error
            assert "HTTP 503 error occurred" in exc_info.value.message
            assert exc_info.value.data is not None
            assert exc_info.value.data["http_status"] == 503


class TestMCPErrorMessageConsistency:
    """Test that error messages are consistent and user-friendly."""

    def test_authentication_error_message_consistency(self):
        """Test that authentication error messages are consistent."""
        error = InvalidRequestError(
            AUTH_REQUIRED,
            data={"http_status": 401},
        )

        assert "Authentication required" in error.message
        assert "start_device_auth" in error.message
        assert error.data is not None
        assert error.data["http_status"] == 401

    def test_not_found_error_message_consistency(self):
        """Test that not found error messages are consistent."""
        error = InvalidRequestError(
            "The requested resource was not found.", data={"http_status": 404}
        )

        assert "not found" in error.message
        assert error.data is not None
        assert error.data["http_status"] == 404

    def test_rate_limit_error_message_consistency(self):
        """Test that rate limit error messages are consistent."""
        error = InvalidRequestError(
            "Rate limit exceeded. Please try again later.", data={"http_status": 429}
        )

        assert "Rate limit exceeded" in error.message
        assert "try again later" in error.message
        assert error.data is not None
        assert error.data["http_status"] == 429

    def test_server_error_message_includes_status_code(self):
        """Test that server error messages include the HTTP status code."""
        error = InternalError(
            "HTTP 500 error occurred",
            data={"http_status": 500, "response": "Internal Server Error"},
        )

        assert "HTTP 500" in error.message
        assert error.data is not None
        assert error.data["http_status"] == 500
        assert error.data is not None
        assert "response" in error.data

    def test_network_error_message_is_user_friendly(self):
        """Test that network error messages are user-friendly."""
        error = InternalError(
            "Unable to connect to Trakt API. Please check your internet connection.",
            data={"error_type": "request_error", "details": "Connection failed"},
        )

        assert "Unable to connect" in error.message
        assert "internet connection" in error.message
        assert error.data is not None
        assert error.data["error_type"] == "request_error"


class TestMCPErrorPropagation:
    """Test that errors propagate correctly through the server layers."""

    @pytest.mark.asyncio
    async def test_errors_propagate_without_modification(self):
        """Test that MCP errors propagate without being modified."""
        from server.movies.tools import fetch_movie_ratings

        original_error = InvalidRequestError(
            "Rate limit exceeded. Please try again later.",
            data={"http_status": 429, "original_context": "test_context"},
        )

        with patch("server.movies.tools.MoviesClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_movie.side_effect = original_error

            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_movie_ratings(movie_id="123")

            # Verify the error is exactly the same as the original
            propagated_error = exc_info.value
            assert propagated_error.message == original_error.message
            assert propagated_error.code == original_error.code
            assert propagated_error.data is not None
            assert original_error.data is not None
            assert propagated_error.data == original_error.data

    @pytest.mark.asyncio
    async def test_client_exceptions_propagate_correctly(self):
        """Test that client method exceptions propagate correctly through server tools."""
        from server.movies.tools import fetch_movie_ratings

        with patch("server.movies.tools.MoviesClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Mock successful first call, exception on second call
            async def async_return_movie():
                return {"title": "Test Movie", "year": 2023}

            mock_client.get_movie.return_value = async_return_movie()

            # Second call raises exception (new architecture)
            async def async_raise_error(*args: Any, **kwargs: Any) -> None:
                raise InvalidRequestError(
                    "Ratings not available for this movie", -32600
                )

            mock_client.get_movie_ratings.side_effect = async_raise_error

            # This should propagate the MCP exception
            with pytest.raises(InvalidRequestError) as exc_info:
                await fetch_movie_ratings(movie_id="123")

            assert exc_info.value.code == -32600
            assert "Ratings not available for this movie" in str(exc_info.value)
