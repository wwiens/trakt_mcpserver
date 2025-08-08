"""Tests for utils.api.error_handler module."""

import uuid
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import MagicMock, patch

import httpx
import pytest

if TYPE_CHECKING:
    from tests.types_stub import MCPErrorWithData
from utils.api.error_handler import TraktAPIErrorHandler, create_correlation_id
from utils.api.error_types import (
    AuthenticationRequiredError,
    AuthorizationPendingError,
    TraktRateLimitError,
    TraktResourceNotFoundError,
    TraktServerError,
    TraktValidationError,
)
from utils.api.errors import InternalError, InvalidParamsError, InvalidRequestError


class TestTraktAPIErrorHandler:
    """Test TraktAPIErrorHandler functionality."""

    @pytest.fixture
    def mock_http_error(self) -> httpx.HTTPStatusError:
        """Create a mock HTTP error for testing."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}

        return httpx.HTTPStatusError(
            message="404 Not Found", request=MagicMock(), response=mock_response
        )

    @patch("utils.api.error_handler.logger")
    def test_handle_http_error_basic(
        self, mock_logger: Any, mock_http_error: httpx.HTTPStatusError
    ) -> None:
        """Test basic HTTP error handling."""
        result = TraktAPIErrorHandler.handle_http_error(mock_http_error)
        result = cast("MCPErrorWithData", result)

        assert isinstance(result, TraktResourceNotFoundError)
        assert result.data["http_status"] == 404
        assert "correlation_id" in result.data
        mock_logger.error.assert_called_once()

    @patch("utils.api.error_handler.logger")
    def test_handle_http_error_with_context(
        self, mock_logger: Any, mock_http_error: httpx.HTTPStatusError
    ) -> None:
        """Test HTTP error handling with context."""
        result = TraktAPIErrorHandler.handle_http_error(
            mock_http_error,
            endpoint="/shows/test",
            resource_type="show",
            resource_id="test-show",
            correlation_id="test-123",
        )
        result = cast("MCPErrorWithData", result)

        assert result.data["endpoint"] == "/shows/test"
        assert result.data["resource_type"] == "show"
        assert result.data["resource_id"] == "test-show"
        assert result.data["correlation_id"] == "test-123"

    @patch("utils.api.error_handler.logger")
    def test_handle_http_error_generates_correlation_id(
        self, mock_logger: Any, mock_http_error: httpx.HTTPStatusError
    ) -> None:
        """Test correlation ID is generated when not provided."""
        result = TraktAPIErrorHandler.handle_http_error(mock_http_error)
        result = cast("MCPErrorWithData", result)
        correlation_id = result.data.get("correlation_id")
        assert correlation_id is not None
        # Should be a valid UUID string
        uuid.UUID(correlation_id)

    @patch("utils.api.error_handler.logger")
    def test_handle_http_error_response_text_error(self, mock_logger: Any) -> None:
        """Test handling when response.text raises an exception."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        # Configure the text property to raise an exception when accessed
        def _raise_text_error(self: Any) -> None:
            raise Exception("Text error")

        type(mock_response).text = property(_raise_text_error)

        http_error = httpx.HTTPStatusError(
            message="500 Error", request=MagicMock(), response=mock_response
        )

        result = TraktAPIErrorHandler.handle_http_error(http_error)
        result = cast("MCPErrorWithData", result)
        assert isinstance(result, TraktServerError)
        # Should handle the exception gracefully


class TestStatusCodeHandlers:
    """Test individual status code handlers."""

    def test_handle_bad_request_generic(self) -> None:
        """Test generic 400 Bad Request handling."""
        result = TraktAPIErrorHandler.handle_bad_request(
            response_text="Generic bad request",
            endpoint="/test",
            correlation_id="test-123",
        )

        assert isinstance(result, InvalidParamsError)
        result = cast("MCPErrorWithData", result)
        assert result.data["http_status"] == 400
        assert result.data["details"] == "Generic bad request"
        assert result.data["endpoint"] == "/test"
        assert result.data["correlation_id"] == "test-123"

    def test_handle_bad_request_authorization_pending(self) -> None:
        """Test 400 Bad Request with authorization_pending."""
        result = TraktAPIErrorHandler.handle_bad_request(
            response_text="authorization_pending - user has not approved",
            resource_id="device123",
        )

        assert isinstance(result, AuthorizationPendingError)
        result = cast("MCPErrorWithData", result)
        assert result.data["device_code"] == "device123"

    def test_handle_bad_request_validation_error(self) -> None:
        """Test 400 Bad Request with validation keywords."""
        result = TraktAPIErrorHandler.handle_bad_request(
            response_text="invalid year parameter"
        )

        assert isinstance(result, TraktValidationError)
        result = cast("MCPErrorWithData", result)
        assert (
            "invalid year parameter"
            in result.data["validation_details"]["api_response"]
        )

    def test_handle_unauthorized(self) -> None:
        """Test 401 Unauthorized handling."""
        result = TraktAPIErrorHandler.handle_unauthorized(resource_type="show")

        assert isinstance(result, AuthenticationRequiredError)
        result = cast("MCPErrorWithData", result)
        assert result.data["action"] == "access show"

    def test_handle_forbidden(self) -> None:
        """Test 403 Forbidden handling."""
        result = TraktAPIErrorHandler.handle_forbidden(
            endpoint="/api/test",
            correlation_id="test-456",
            response_text="Forbidden access",
        )

        assert isinstance(result, InvalidRequestError)
        result = cast("MCPErrorWithData", result)
        assert result.data["http_status"] == 403
        assert result.data["endpoint"] == "/api/test"
        assert result.data["correlation_id"] == "test-456"
        assert result.data["details"] == "Forbidden access"

    def test_handle_not_found(self) -> None:
        """Test 404 Not Found handling."""
        result = TraktAPIErrorHandler.handle_not_found(
            resource_type="movie",
            resource_id="inception",
            endpoint="/movies/inception",
            correlation_id="test-789",
        )

        assert isinstance(result, TraktResourceNotFoundError)
        result = cast("MCPErrorWithData", result)
        assert result.data["resource_type"] == "movie"
        assert result.data["resource_id"] == "inception"
        assert result.data["endpoint"] == "/movies/inception"
        assert result.data["correlation_id"] == "test-789"

    def test_handle_not_found_defaults(self) -> None:
        """Test 404 handling with default values."""
        result = TraktAPIErrorHandler.handle_not_found()

        assert isinstance(result, TraktResourceNotFoundError)
        result = cast("MCPErrorWithData", result)
        assert result.data["resource_type"] == "resource"
        assert result.data["resource_id"] == "unknown"

    def test_handle_conflict(self) -> None:
        """Test 409 Conflict handling."""
        result = TraktAPIErrorHandler.handle_conflict(
            endpoint="/checkins",
            resource_type="checkin",
            resource_id="show-123",
            correlation_id="test-conflict",
            response_text="Already checked in",
        )

        assert isinstance(result, InvalidRequestError)
        result = cast("MCPErrorWithData", result)
        assert result.data["http_status"] == 409
        assert result.data["endpoint"] == "/checkins"
        assert result.data["resource_type"] == "checkin"
        assert result.data["resource_id"] == "show-123"
        assert result.data["correlation_id"] == "test-conflict"
        assert result.data["details"] == "Already checked in"

    def test_handle_validation_error(self) -> None:
        """Test 422 Unprocessable Entity handling."""
        result = TraktAPIErrorHandler.handle_validation_error(
            response_text="Validation failed: invalid year",
            endpoint="/shows",
            correlation_id="test-validation",
        )

        assert isinstance(result, TraktValidationError)
        result = cast("MCPErrorWithData", result)
        assert (
            result.data["validation_details"]["api_response"]
            == "Validation failed: invalid year"
        )
        assert result.data["validation_details"]["endpoint"] == "/shows"
        assert result.data["validation_details"]["correlation_id"] == "test-validation"

    def test_handle_rate_limit_without_retry_after(self) -> None:
        """Test 429 Rate Limit handling without retry-after header."""
        result = TraktAPIErrorHandler.handle_rate_limit(
            endpoint="/shows/trending", correlation_id="test-rate-limit"
        )

        assert isinstance(result, TraktRateLimitError)
        result = cast("MCPErrorWithData", result)
        assert "retry_after" not in result.data
        assert result.data["endpoint"] == "/shows/trending"
        assert result.data["correlation_id"] == "test-rate-limit"

    def test_handle_rate_limit_with_retry_after(self) -> None:
        """Test 429 Rate Limit handling with retry-after header."""
        mock_response = MagicMock()
        mock_response.headers = {"retry-after": "60"}
        mock_error = MagicMock()
        mock_error.response = mock_response

        result = TraktAPIErrorHandler.handle_rate_limit(
            error=mock_error, endpoint="/movies/popular"
        )

        assert isinstance(result, TraktRateLimitError)
        result = cast("MCPErrorWithData", result)
        assert result.data["retry_after"] == 60
        assert result.data["endpoint"] == "/movies/popular"

    def test_handle_rate_limit_invalid_retry_after(self) -> None:
        """Test 429 Rate Limit handling with invalid retry-after header."""
        mock_response = MagicMock()
        mock_response.headers = {"retry-after": "invalid"}
        mock_error = MagicMock()
        mock_error.response = mock_response

        result = TraktAPIErrorHandler.handle_rate_limit(error=mock_error)

        assert isinstance(result, TraktRateLimitError)
        result = cast("MCPErrorWithData", result)
        assert "retry_after" not in result.data

    def test_handle_server_error(self) -> None:
        """Test 500 Internal Server Error handling."""
        result = TraktAPIErrorHandler.handle_server_error(
            endpoint="/api/shows", correlation_id="test-500"
        )

        assert isinstance(result, TraktServerError)
        result = cast("MCPErrorWithData", result)
        assert result.data["http_status"] == 500
        assert result.data["endpoint"] == "/api/shows"
        assert result.data["correlation_id"] == "test-500"

    def test_handle_bad_gateway(self) -> None:
        """Test 502 Bad Gateway handling."""
        result = TraktAPIErrorHandler.handle_bad_gateway(
            endpoint="/api/movies", correlation_id="test-502"
        )

        assert isinstance(result, TraktServerError)
        result = cast("MCPErrorWithData", result)
        assert result.data["http_status"] == 502
        assert result.data["endpoint"] == "/api/movies"
        assert result.data["correlation_id"] == "test-502"
        assert "bad gateway" in result.message.lower()

    def test_handle_service_unavailable(self) -> None:
        """Test 503 Service Unavailable handling."""
        result = TraktAPIErrorHandler.handle_service_unavailable(
            endpoint="/api/users", correlation_id="test-503"
        )

        assert isinstance(result, TraktServerError)
        result = cast("MCPErrorWithData", result)
        assert result.data["http_status"] == 503
        assert result.data["endpoint"] == "/api/users"
        assert result.data["correlation_id"] == "test-503"
        assert "service unavailable" in result.message.lower()

    def test_handle_unknown_error(self) -> None:
        """Test unknown status code handling."""
        mock_response = MagicMock()
        mock_response.status_code = 418  # I'm a teapot
        mock_error = MagicMock()
        mock_error.response = mock_response

        result = TraktAPIErrorHandler.handle_unknown_error(
            error=mock_error,
            endpoint="/api/teapot",
            resource_type="teapot",
            resource_id="tea123",
            correlation_id="test-418",
            response_text="I'm a teapot",
        )

        assert isinstance(result, InternalError)
        result = cast("MCPErrorWithData", result)
        assert result.data["http_status"] == 418
        assert result.data["endpoint"] == "/api/teapot"
        assert result.data["resource_type"] == "teapot"
        assert result.data["resource_id"] == "tea123"
        assert result.data["correlation_id"] == "test-418"
        assert result.data["response"] == "I'm a teapot"

    def test_handle_unknown_error_no_error_object(self) -> None:
        """Test unknown error handling without error object."""
        result = TraktAPIErrorHandler.handle_unknown_error(
            correlation_id="test-unknown"
        )

        assert isinstance(result, InternalError)
        result = cast("MCPErrorWithData", result)
        assert result.data["http_status"] == "unknown"
        assert result.data["correlation_id"] == "test-unknown"


class TestStatusCodeMapping:
    """Test status code to handler mapping."""

    def test_get_status_code_handler_known_codes(self) -> None:
        """Test mapping for known status codes."""
        test_cases = [
            (400, TraktAPIErrorHandler.handle_bad_request),
            (401, TraktAPIErrorHandler.handle_unauthorized),
            (403, TraktAPIErrorHandler.handle_forbidden),
            (404, TraktAPIErrorHandler.handle_not_found),
            (409, TraktAPIErrorHandler.handle_conflict),
            (422, TraktAPIErrorHandler.handle_validation_error),
            (429, TraktAPIErrorHandler.handle_rate_limit),
            (500, TraktAPIErrorHandler.handle_server_error),
            (502, TraktAPIErrorHandler.handle_bad_gateway),
            (503, TraktAPIErrorHandler.handle_service_unavailable),
        ]

        for status_code, expected_handler in test_cases:
            handler = TraktAPIErrorHandler.get_status_code_handler(status_code)
            assert handler == expected_handler

    def test_get_status_code_handler_unknown_code(self) -> None:
        """Test mapping for unknown status codes."""
        handler = TraktAPIErrorHandler.get_status_code_handler(418)
        assert handler == TraktAPIErrorHandler.handle_unknown_error


class TestLogging:
    """Test error logging functionality."""

    @patch("utils.api.error_handler.logger")
    def test_log_http_error_basic(self, mock_logger: Any) -> None:
        """Test basic HTTP error logging."""
        TraktAPIErrorHandler.log_http_error(
            status_code=404,
            endpoint="/shows/test",
            resource_type="show",
            resource_id="test-show",
            correlation_id="test-123",
            response_text="Not found",
        )

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args

        # Check log message
        assert "404" in call_args[0][0]

        # Check context data
        context = call_args[1]["extra"]["context"]
        assert context["http_status"] == 404
        assert context["endpoint"] == "/shows/test"
        assert context["resource_type"] == "show"
        assert context["resource_id"] == "test-show"
        assert context["correlation_id"] == "test-123"
        assert context["response_length"] == len("Not found")
        assert context["response_preview"] == "Not found"

    @patch("utils.api.error_handler.logger")
    def test_log_http_error_truncated_response(self, mock_logger: Any) -> None:
        """Test logging with long response text that gets truncated."""
        long_response = "x" * 300  # Longer than 200 chars

        TraktAPIErrorHandler.log_http_error(
            status_code=500,
            endpoint=None,
            resource_type=None,
            resource_id=None,
            correlation_id="test-truncate",
            response_text=long_response,
        )

        mock_logger.error.assert_called_once()
        context = mock_logger.error.call_args[1]["extra"]["context"]

        assert context["response_length"] == 300
        assert len(context["response_preview"]) == 203  # 200 + "..."
        assert context["response_preview"].endswith("...")

    @patch("utils.api.error_handler.logger")
    def test_log_http_error_minimal_context(self, mock_logger: Any) -> None:
        """Test logging with minimal context."""
        TraktAPIErrorHandler.log_http_error(
            status_code=400,
            endpoint=None,
            resource_type=None,
            resource_id=None,
            correlation_id="minimal-test",
            response_text="",
        )

        mock_logger.error.assert_called_once()
        context = mock_logger.error.call_args[1]["extra"]["context"]

        assert context["http_status"] == 400
        assert context["correlation_id"] == "minimal-test"
        assert context["response_length"] == 0
        assert context["response_preview"] == ""

        # Optional keys should not be present
        assert "endpoint" not in context
        assert "resource_type" not in context
        assert "resource_id" not in context


class TestCorrelationId:
    """Test correlation ID functionality."""

    def test_create_correlation_id(self) -> None:
        """Test correlation ID creation."""
        correlation_id = create_correlation_id()

        assert isinstance(correlation_id, str)
        # Should be a valid UUID
        uuid.UUID(correlation_id)

    def test_create_correlation_id_unique(self) -> None:
        """Test correlation IDs are unique."""
        id1 = create_correlation_id()
        id2 = create_correlation_id()

        assert id1 != id2


class TestIntegration:
    """Test integration scenarios."""

    @patch("utils.api.error_handler.logger")
    def test_handle_http_error_end_to_end_404(self, mock_logger: Any) -> None:
        """Test complete 404 error handling flow."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Show not found"

        http_error = httpx.HTTPStatusError(
            message="404 Not Found", request=MagicMock(), response=mock_response
        )

        result = TraktAPIErrorHandler.handle_http_error(
            error=http_error,
            endpoint="/shows/nonexistent",
            resource_type="show",
            resource_id="nonexistent",
            correlation_id="integration-test-404",
        )
        result = cast("MCPErrorWithData", result)
        # Check error type and properties
        assert isinstance(result, TraktResourceNotFoundError)
        assert result.data["resource_type"] == "show"
        assert result.data["resource_id"] == "nonexistent"
        assert result.data["endpoint"] == "/shows/nonexistent"
        assert result.data["correlation_id"] == "integration-test-404"

        # Check logging was called
        mock_logger.error.assert_called_once()

    @patch("utils.api.error_handler.logger")
    def test_handle_http_error_end_to_end_429(self, mock_logger: Any) -> None:
        """Test complete 429 rate limit error handling flow."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.headers = {"retry-after": "120"}

        http_error = httpx.HTTPStatusError(
            message="429 Too Many Requests", request=MagicMock(), response=mock_response
        )

        result = TraktAPIErrorHandler.handle_http_error(
            error=http_error,
            endpoint="/shows/trending",
            correlation_id="integration-test-429",
        )
        result = cast("MCPErrorWithData", result)
        # Check error type and properties
        assert isinstance(result, TraktRateLimitError)
        assert result.data["http_status"] == 429
        assert result.data["retry_after"] == 120
        assert result.data["endpoint"] == "/shows/trending"
        assert result.data["correlation_id"] == "integration-test-429"

        # Check logging was called
        mock_logger.error.assert_called_once()
