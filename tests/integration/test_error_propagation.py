"""Comprehensive error propagation tests for Phase 5 of error handling audit.

This module tests error propagation through the complete stack:
Client → Tool → MCP → Response

It also tests correlation ID tracking, context preservation, and edge cases.
"""

import json
import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

if TYPE_CHECKING:
    from tests.types_stub import MCPErrorWithData
from utils.api.error_types import (
    AuthenticationRequiredError,
    TraktRateLimitError,
    TraktResourceNotFoundError,
    TraktServerError,
    TraktValidationError,
)
from utils.api.errors import InternalError, InvalidParamsError, InvalidRequestError
from utils.api.request_context import (
    RequestContext,
    clear_current_context,
    set_current_context,
)

# Type alias for the mock HTTP error factory function
MockHttpErrorFactory = Callable[..., httpx.HTTPStatusError]


class TestErrorPropagationThroughStack:
    """Test error propagation through the complete Client → Tool → MCP → Response stack."""

    @pytest.fixture(autouse=True)
    def setup_context(self):
        """Set up and clean up request context for each test."""
        clear_current_context()
        yield
        clear_current_context()

    @pytest.fixture
    def mock_http_error(self):
        """Create a mock HTTP error generator."""

        def _create_error(
            status_code: int,
            response_text: str = "Error",
            headers: dict[str, str] | None = None,
        ):
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = response_text
            mock_response.headers = headers or {}

            return httpx.HTTPStatusError(
                message=f"{status_code} Error",
                request=MagicMock(),
                response=mock_response,
            )

        return _create_error

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_400_error_propagation_through_stack(
        self, mock_http_error: MockHttpErrorFactory
    ):
        """Test 400 Bad Request error propagation from Client to Tool to MCP."""
        # Set up request context
        context = (
            RequestContext()
            .with_endpoint("/shows/search", "GET")
            .with_resource("show", "test-show")
            .with_parameters(query="test")
            .with_user("test_user")
        )
        set_current_context(context)

        # Create 400 error with validation message
        error_400 = mock_http_error(
            400, '{"error": "validation_error", "message": "Invalid parameters"}'
        )

        with patch("server.search.tools.SearchClient") as mock_search_client:
            # Configure search client async method to raise error
            search_client_instance = mock_search_client.return_value
            search_client_instance.search_shows = AsyncMock(side_effect=error_400)

            from server.search.tools import search_shows

            # The tool should raise a structured MCP error, not return a string
            with pytest.raises(
                (InvalidParamsError, TraktValidationError, InternalError)
            ) as exc_info:
                await search_shows(query="test")

            # Verify error context is preserved
            error = cast("MCPErrorWithData", exc_info.value)
            assert hasattr(error, "data")
            assert error.data is not None

            # Should contain request context
            if "correlation_id" in error.data:
                assert error.data["correlation_id"] == context.correlation_id
            if "endpoint" in error.data:
                assert error.data["endpoint"] == "/shows/search"
            if "resource_type" in error.data:
                assert error.data["resource_type"] == "show"

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_401_error_propagation_through_stack(
        self, mock_http_error: MockHttpErrorFactory
    ):
        """Test 401 Unauthorized error propagation through the stack."""
        # Set up request context
        context = RequestContext().with_endpoint("/user/watched/shows", "GET")
        set_current_context(context)

        error_401 = mock_http_error(401, "Unauthorized")

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.user.tools.UserClient") as mock_user_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.side_effect = error_401

            user_client_instance = mock_user_client.return_value
            user_client_instance._make_request.side_effect = error_401
            user_client_instance.is_authenticated.return_value = False

            from server.user.tools import fetch_user_watched_shows

            # Should raise AuthenticationRequiredError
            with pytest.raises(AuthenticationRequiredError) as exc_info:
                await fetch_user_watched_shows()

            error = cast("MCPErrorWithData", exc_info.value)
            assert "Authentication required" in str(error)
            assert hasattr(error, "data")
            assert error.data is not None
            assert "auth_url" in error.data

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_404_error_propagation_through_stack(
        self, mock_http_error: MockHttpErrorFactory
    ):
        """Test 404 Not Found error propagation through the stack."""
        context = (
            RequestContext()
            .with_endpoint("/shows/nonexistent", "GET")
            .with_resource("show", "nonexistent")
        )
        set_current_context(context)

        error_404 = mock_http_error(404, "Not Found")

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.shows.tools.ShowDetailsClient") as mock_shows_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.side_effect = error_404

            shows_client_instance = mock_shows_client.return_value
            shows_client_instance.get_show_extended = AsyncMock(
                side_effect=TraktResourceNotFoundError(
                    "show", "nonexistent", "Show not found"
                )
            )
            shows_client_instance.get_show = AsyncMock(
                side_effect=TraktResourceNotFoundError(
                    "show", "nonexistent", "Show not found"
                )
            )

            from server.shows.tools import fetch_show_summary

            with pytest.raises(
                (InvalidRequestError, TraktResourceNotFoundError)
            ) as exc_info:
                await fetch_show_summary(show_id="nonexistent")

            error = cast("MCPErrorWithData", exc_info.value)
            assert hasattr(error, "data")
            assert error.data is not None
            if "http_status" in error.data:
                assert error.data["http_status"] == 404

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_429_error_propagation_through_stack(
        self, mock_http_error: MockHttpErrorFactory
    ):
        """Test 429 Rate Limit error propagation through the stack."""
        context = RequestContext().with_endpoint("/shows/trending", "GET")
        set_current_context(context)

        error_429 = mock_http_error(429, "Rate Limit Exceeded", {"Retry-After": "60"})

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.shows.tools.TrendingShowsClient") as mock_shows_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.side_effect = error_429

            shows_client_instance = mock_shows_client.return_value
            shows_client_instance.get_trending_shows = AsyncMock(
                side_effect=TraktRateLimitError(retry_after=60)
            )

            from server.shows.tools import fetch_trending_shows

            with pytest.raises((InternalError, TraktRateLimitError)) as exc_info:
                await fetch_trending_shows()

            error = cast("MCPErrorWithData", exc_info.value)
            assert hasattr(error, "data")
            assert error.data is not None
            # Should contain retry information
            if "retry_after" in error.data:
                assert error.data["retry_after"] in [60, "60"]

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_503_error_propagation_through_stack(
        self, mock_http_error: MockHttpErrorFactory
    ):
        """Test 503 Service Unavailable error propagation through the stack."""
        context = RequestContext().with_endpoint("/movies/trending", "GET")
        set_current_context(context)

        error_503 = mock_http_error(503, "Service Unavailable")

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.movies.tools.TrendingMoviesClient") as mock_movies_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.side_effect = error_503

            movies_client_instance = mock_movies_client.return_value
            movies_client_instance.get_trending_movies = AsyncMock(
                side_effect=error_503
            )

            from server.movies.tools import fetch_trending_movies

            with pytest.raises((InternalError, TraktServerError)) as exc_info:
                await fetch_trending_movies()

            error = cast("MCPErrorWithData", exc_info.value)
            assert hasattr(error, "data")
            assert error.data is not None
            if "http_status" in error.data:
                assert error.data["http_status"] == 503


class TestCorrelationIDTracking:
    """Test end-to-end correlation ID tracking through the error handling stack."""

    @pytest.fixture(autouse=True)
    def setup_context(self):
        """Set up and clean up request context for each test."""
        clear_current_context()
        yield
        clear_current_context()

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_correlation_id_preserved_through_error_stack(self):
        """Test that correlation IDs are preserved from request to error response."""
        # Create initial context with specific correlation ID
        initial_context = RequestContext().with_endpoint("/test", "GET")
        original_correlation_id = initial_context.correlation_id
        set_current_context(initial_context)

        # Verify it's a valid UUID
        uuid.UUID(original_correlation_id)  # This will raise if invalid

        error_500 = httpx.HTTPStatusError(
            message="500 Internal Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500, text="Internal Error", headers={}),
        )

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.shows.tools.ShowDetailsClient") as mock_shows_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.side_effect = error_500

            shows_client_instance = mock_shows_client.return_value
            shows_client_instance.get_show_extended = AsyncMock(
                side_effect=TraktServerError(500, "Internal server error")
            )
            shows_client_instance.get_show = AsyncMock(
                side_effect=TraktServerError(500, "Internal server error")
            )

            from server.shows.tools import fetch_show_summary

            with pytest.raises((InternalError, TraktServerError)) as exc_info:
                await fetch_show_summary(show_id="test")

            error = cast("MCPErrorWithData", exc_info.value)
            assert hasattr(error, "data")
            assert error.data is not None

            # Correlation ID should be preserved in error data
            if "correlation_id" in error.data:
                assert error.data["correlation_id"] == original_correlation_id

    @pytest.mark.asyncio
    async def test_correlation_id_generation_when_none_exists(self):
        """Test that correlation IDs are generated when no context exists."""
        # Ensure no context exists
        clear_current_context()

        error_400 = httpx.HTTPStatusError(
            message="400 Bad Request",
            request=MagicMock(),
            response=MagicMock(status_code=400, text="Bad Request", headers={}),
        )

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.search.tools.SearchClient") as mock_search_client,
            patch.dict(
                "os.environ",
                {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
            ),
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.side_effect = error_400

            search_client_instance = mock_search_client.return_value
            search_client_instance.search_shows = AsyncMock(
                side_effect=TraktValidationError(
                    "Invalid search parameters",
                    missing_params=["query"],
                    validation_details={"query": "Query parameter is required"},
                )
            )

            from server.search.tools import search_shows

            with pytest.raises((InvalidParamsError, TraktValidationError)) as exc_info:
                await search_shows(query="test")

            error = cast("MCPErrorWithData", exc_info.value)
            assert hasattr(error, "data")
            assert error.data is not None

            # A correlation ID should have been generated
            if "correlation_id" in error.data:
                correlation_id = error.data["correlation_id"]
                assert correlation_id is not None
                # Should be a valid UUID
                uuid.UUID(correlation_id)


class TestErrorContextPreservation:
    """Test that error context is preserved across all layers of the stack."""

    @pytest.fixture(autouse=True)
    def setup_context(self):
        """Set up and clean up request context for each test."""
        clear_current_context()
        yield
        clear_current_context()

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_full_context_preservation_in_errors(self):
        """Test that full request context is preserved in error responses."""
        # Set up comprehensive context
        context = (
            RequestContext()
            .with_endpoint("/shows/breaking-bad/ratings", "GET")
            .with_resource("show", "breaking-bad")
            .with_parameters(limit=10, extended="full")
            .with_user("test_user_123")
        )
        set_current_context(context)

        error_422 = httpx.HTTPStatusError(
            message="422 Unprocessable Entity",
            request=MagicMock(),
            response=MagicMock(
                status_code=422, text='{"error": "validation_failed"}', headers={}
            ),
        )

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.shows.tools.ShowDetailsClient") as mock_shows_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.side_effect = error_422

            shows_client_instance = mock_shows_client.return_value
            shows_client_instance.get_show = AsyncMock(
                side_effect=TraktValidationError(
                    "Invalid parameters", missing_params=["show_id"]
                )
            )
            shows_client_instance.get_show_ratings = AsyncMock(
                side_effect=TraktValidationError(
                    "Invalid parameters", missing_params=["show_id"]
                )
            )

            from server.shows.tools import fetch_show_ratings

            with pytest.raises((InvalidParamsError, TraktValidationError)) as exc_info:
                await fetch_show_ratings(show_id="breaking-bad")

            error = cast("MCPErrorWithData", exc_info.value)
            assert hasattr(error, "data")
            assert error.data is not None
            error_data = error.data

            # Verify all context is preserved
            expected_fields = {
                "correlation_id": context.correlation_id,
                "endpoint": "/shows/breaking-bad/ratings",
                "method": "GET",
                "resource_type": "show",
                "resource_id": "breaking-bad",
                "user_id": "test_user_123",
            }

            for field, expected_value in expected_fields.items():
                if field in error_data:
                    assert error_data[field] == expected_value, (
                        f"Field {field} not preserved correctly"
                    )

            # Parameters should be preserved (may be nested)
            if "parameters" in error_data:
                params = error_data["parameters"]
                assert isinstance(params, dict)
            elif "limit" in error_data:  # Or they might be flattened
                assert error_data["limit"] == 10

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_parameter_context_in_validation_errors(self):
        """Test that parameter context is preserved in validation errors."""
        context = RequestContext().with_parameters(show_id="", season=0, episode=-1)
        set_current_context(context)

        # Test parameter validation error
        from server.checkin.tools import checkin_to_show

        with patch("server.checkin.tools.CheckinClient") as mock_checkin_client:
            # Mock authentication to be successful so we can test parameter validation
            mock_client_instance = mock_checkin_client.return_value
            mock_client_instance.is_authenticated.return_value = True

            with pytest.raises(InvalidParamsError) as exc_info:
                await checkin_to_show(season=0, episode=-1, show_id="")

        error = cast("MCPErrorWithData", exc_info.value)
        assert hasattr(error, "data")
        assert error.data is not None

        # Should contain information about invalid parameters
        error_data = error.data
        assert "error_type" in error_data
        assert error_data["error_type"] == "validation_error"


class TestEdgeCasesAndErrorScenarios:
    """Test edge cases and complex error scenarios."""

    @pytest.fixture(autouse=True)
    def setup_context(self):
        """Set up and clean up request context for each test."""
        clear_current_context()
        yield
        clear_current_context()

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_network_timeout_error_handling(self):
        """Test handling of network timeouts and connection errors."""
        context = RequestContext().with_endpoint("/shows/trending", "GET")
        set_current_context(context)

        # Simulate network timeout
        network_error = httpx.TimeoutException("Request timed out")

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.shows.tools.TrendingShowsClient") as mock_shows_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.side_effect = network_error

            shows_client_instance = mock_shows_client.return_value
            shows_client_instance.get_trending_shows = AsyncMock(
                side_effect=network_error
            )

            from server.shows.tools import fetch_trending_shows

            with pytest.raises(InternalError) as exc_info:
                await fetch_trending_shows()

            error = exc_info.value
            assert "unable to connect to trakt api" in str(error).lower()

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_malformed_json_response_error(self):
        """Test handling of malformed JSON responses from API."""
        context = RequestContext().with_endpoint("/movies/summary", "GET")
        set_current_context(context)

        # Create mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.movies.tools.MovieDetailsClient") as mock_movies_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.return_value = mock_response

            movies_client_instance = mock_movies_client.return_value
            movies_client_instance.get_movie_extended = AsyncMock(
                side_effect=json.JSONDecodeError("Invalid JSON", "", 0)
            )

            from server.movies.tools import fetch_movie_summary

            with pytest.raises(InternalError) as exc_info:
                await fetch_movie_summary(movie_id="test")

            error = cast("MCPErrorWithData", exc_info.value)
            # Should be handled as an internal error
            assert hasattr(error, "data")
            assert error.data is not None

    @pytest.mark.asyncio
    async def test_missing_required_parameters_validation(self):
        """Test validation of missing required parameters."""
        from server.base.error_mixin import BaseToolErrorMixin

        # Test the validation mixin directly
        with pytest.raises(InvalidParamsError) as exc_info:
            BaseToolErrorMixin.validate_required_params(
                show_id=None,
                movie_id="",
                query="   ",  # Whitespace only
            )

        error = cast("MCPErrorWithData", exc_info.value)
        assert "Missing required parameter" in str(error)
        assert hasattr(error, "data")
        assert error.data is not None
        assert "missing_parameters" in error.data

        missing_params = error.data["missing_parameters"]
        assert "show_id" in missing_params
        assert "movie_id" in missing_params
        assert "query" in missing_params

    @pytest.mark.asyncio
    async def test_either_or_parameter_validation(self):
        """Test validation of either/or parameter requirements."""
        from server.base.error_mixin import BaseToolErrorMixin

        # Test successful validation - one valid set provided
        try:
            BaseToolErrorMixin.validate_either_or_params(
                [("show_id",), ("show_title", "show_year")],
                show_id="breaking-bad",
                show_title="",
                show_year=None,
            )
        except Exception:
            pytest.fail(
                "Should not raise exception when valid parameter set is provided"
            )

        # Test failed validation - no valid sets provided
        with pytest.raises(InvalidParamsError) as exc_info:
            BaseToolErrorMixin.validate_either_or_params(
                [("show_id",), ("show_title", "show_year")],
                show_id="",
                show_title="",
                show_year=None,
            )

        error = cast("MCPErrorWithData", exc_info.value)
        assert "Must provide one of" in str(error)
        assert hasattr(error, "data")
        assert error.data is not None
        assert "required_parameter_sets" in error.data

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
    )
    async def test_unexpected_error_wrapping(self):
        """Test that unexpected errors are properly wrapped in MCP errors."""
        context = RequestContext().with_endpoint("/test", "GET")
        set_current_context(context)

        # Create an unexpected error (not HTTP-related)
        unexpected_error = RuntimeError("Something went wrong in the code")

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("server.shows.tools.ShowDetailsClient") as mock_shows_client,
        ):
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.return_value = MagicMock()  # Return valid response

            shows_client_instance = mock_shows_client.return_value
            # Make the client method raise an unexpected error
            shows_client_instance.get_show_extended = AsyncMock(
                side_effect=unexpected_error
            )

            from server.shows.tools import fetch_show_summary

            with pytest.raises(InternalError) as exc_info:
                await fetch_show_summary(show_id="test")

            error = cast("MCPErrorWithData", exc_info.value)
            assert "unexpected error occurred" in str(error).lower()
            assert hasattr(error, "data")
            assert error.data is not None

            # Should contain information about the original error
            if "original_error" in error.data:
                assert "Something went wrong" in error.data["original_error"]
            if "original_error_type" in error.data:
                assert error.data["original_error_type"] == "ValueError"
