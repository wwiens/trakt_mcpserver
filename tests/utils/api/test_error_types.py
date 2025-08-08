"""Tests for utils.api.error_types module."""

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from tests.types_stub import MCPErrorWithData
from utils.api.error_types import (
    AuthenticationRequiredError,
    AuthorizationPendingError,
    TraktAPIError,
    TraktRateLimitError,
    TraktResourceNotFoundError,
    TraktServerError,
    TraktValidationError,
)
from utils.api.errors import InvalidParamsError, InvalidRequestError, MCPError


class TestTraktAPIError:
    """Test TraktAPIError base class."""

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        error = TraktAPIError(
            code=-32600,
            message="Test error",
        )
        error = cast("MCPErrorWithData", error)
        assert error.code == -32600
        assert error.message == "Test error"
        assert error.data == {}

    def test_init_with_data(self) -> None:
        """Test initialization with basic data."""
        error = TraktAPIError(
            code=-32600,
            message="Test error",
            data={"custom": "data"},
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["custom"] == "data"

    def test_init_with_context(self) -> None:
        """Test initialization with rich context."""
        error = TraktAPIError(
            code=-32600,
            message="Test error",
            endpoint="/shows/breaking-bad",
            resource_type="show",
            resource_id="breaking-bad",
            correlation_id="test-123",
            http_status=404,
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["endpoint"] == "/shows/breaking-bad"
        assert error.data["resource_type"] == "show"
        assert error.data["resource_id"] == "breaking-bad"
        assert error.data["correlation_id"] == "test-123"
        assert error.data["http_status"] == 404

    def test_init_with_data_and_context(self) -> None:
        """Test initialization with both data and context."""
        error = TraktAPIError(
            code=-32600,
            message="Test error",
            data={"custom": "data"},
            endpoint="/shows/test",
            resource_type="show",
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["custom"] == "data"
        assert error.data["endpoint"] == "/shows/test"
        assert error.data["resource_type"] == "show"

    def test_to_dict(self) -> None:
        """Test error serialization to dictionary."""
        error = TraktAPIError(
            code=-32600,
            message="Test error",
            data={"test": "data"},
            endpoint="/test",
        )
        result = error.to_dict()

        assert result["code"] == -32600
        assert result["message"] == "Test error"
        assert result["data"]["test"] == "data"
        assert result["data"]["endpoint"] == "/test"


class TestAuthenticationRequiredError:
    """Test AuthenticationRequiredError class."""

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        error = AuthenticationRequiredError("access shows")
        error = cast("MCPErrorWithData", error)
        assert error.code == -32600  # InvalidRequestError code
        assert error.message == "Authentication required to access shows"
        assert error.data["error_type"] == "auth_required"
        assert error.data["action"] == "access shows"
        assert "auth_url" in error.data
        assert "instructions" in error.data

    def test_init_with_custom_auth_url(self) -> None:
        """Test initialization with custom auth URL."""
        error = AuthenticationRequiredError(
            "access movies", auth_url="https://custom.url/auth"
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["auth_url"] == "https://custom.url/auth"
        assert error.data["action"] == "access movies"

    def test_init_with_custom_message(self) -> None:
        """Test initialization with custom message."""
        error = AuthenticationRequiredError(
            "test action", message="Custom auth message"
        )
        error = cast("MCPErrorWithData", error)
        assert error.message == "Custom auth message"
        assert error.data["action"] == "test action"

    def test_inheritance(self) -> None:
        """Test proper inheritance chain."""
        error = AuthenticationRequiredError("test")
        error = cast("MCPErrorWithData", error)
        assert isinstance(error, InvalidRequestError)
        assert isinstance(error, MCPError)


class TestAuthorizationPendingError:
    """Test AuthorizationPendingError class."""

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        error = AuthorizationPendingError()

        assert error.code == -32001
        assert error.message == "Authorization pending. User must approve device code."
        error = cast("MCPErrorWithData", error)
        assert error.data["error_type"] == "auth_pending"

    def test_init_with_device_code(self) -> None:
        """Test initialization with device code."""
        error = AuthorizationPendingError(device_code="ABC123")
        error = cast("MCPErrorWithData", error)
        assert error.data["device_code"] == "ABC123"
        assert error.data["error_type"] == "auth_pending"

    def test_init_with_expires_in(self) -> None:
        """Test initialization with expiry time."""
        error = AuthorizationPendingError(expires_in=600)
        error = cast("MCPErrorWithData", error)
        assert error.data["expires_in"] == 600
        assert error.data["error_type"] == "auth_pending"

    def test_init_with_all_params(self) -> None:
        """Test initialization with all parameters."""
        error = AuthorizationPendingError(device_code="XYZ789", expires_in=300)
        error = cast("MCPErrorWithData", error)
        assert error.data["device_code"] == "XYZ789"
        assert error.data["expires_in"] == 300

    def test_inheritance(self) -> None:
        """Test proper inheritance chain."""
        error = AuthorizationPendingError()

        assert isinstance(error, MCPError)


class TestTraktValidationError:
    """Test TraktValidationError class."""

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        error = TraktValidationError("Validation failed")
        error = cast("MCPErrorWithData", error)
        assert error.code == -32602  # InvalidParamsError code
        assert error.message == "Validation failed"
        assert error.data["error_type"] == "validation_error"

    def test_init_with_invalid_params(self) -> None:
        """Test initialization with invalid parameters list."""
        error = TraktValidationError(
            "Validation failed", invalid_params=["year", "rating"]
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["invalid_params"] == ["year", "rating"]

    def test_init_with_missing_params(self) -> None:
        """Test initialization with missing parameters list."""
        error = TraktValidationError(
            "Validation failed", missing_params=["title", "imdb_id"]
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["missing_params"] == ["title", "imdb_id"]

    def test_init_with_validation_details(self) -> None:
        """Test initialization with validation details."""
        details = {
            "year": "Must be between 1900 and 2024",
            "rating": "Must be between 1 and 10",
        }
        error = TraktValidationError("Validation failed", validation_details=details)
        error = cast("MCPErrorWithData", error)
        assert error.data["validation_details"] == details

    def test_init_with_all_params(self) -> None:
        """Test initialization with all parameters."""
        error = TraktValidationError(
            "Multiple validation errors",
            invalid_params=["year"],
            missing_params=["title"],
            validation_details={"year": "Invalid year"},
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["invalid_params"] == ["year"]
        assert error.data["missing_params"] == ["title"]
        assert error.data["validation_details"]["year"] == "Invalid year"

    def test_inheritance(self) -> None:
        """Test proper inheritance chain."""
        error = TraktValidationError("test")
        error = cast("MCPErrorWithData", error)
        assert isinstance(error, InvalidParamsError)
        assert isinstance(error, MCPError)


class TestTraktResourceNotFoundError:
    """Test TraktResourceNotFoundError class."""

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        error = TraktResourceNotFoundError("show", "breaking-bad")
        error = cast("MCPErrorWithData", error)
        assert error.code == -32600  # Invalid request
        assert error.message == "The requested show 'breaking-bad' was not found"
        assert error.data["resource_type"] == "show"
        assert error.data["resource_id"] == "breaking-bad"
        assert error.data["http_status"] == 404

    def test_init_with_custom_message(self) -> None:
        """Test initialization with custom message."""
        error = TraktResourceNotFoundError(
            "movie", "inception", message="Custom not found message"
        )
        error = cast("MCPErrorWithData", error)
        assert error.message == "Custom not found message"
        assert error.data["resource_type"] == "movie"
        assert error.data["resource_id"] == "inception"

    def test_init_with_context(self) -> None:
        """Test initialization with additional context."""
        error = TraktResourceNotFoundError(
            "user", "testuser", endpoint="/users/testuser", correlation_id="test-123"
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["endpoint"] == "/users/testuser"
        assert error.data["correlation_id"] == "test-123"

    def test_inheritance(self) -> None:
        """Test proper inheritance chain."""
        error = TraktResourceNotFoundError("show", "test")
        error = cast("MCPErrorWithData", error)
        assert isinstance(error, TraktAPIError)
        assert isinstance(error, MCPError)


class TestTraktRateLimitError:
    """Test TraktRateLimitError class."""

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        error = TraktRateLimitError()

        assert error.code == -32600  # Invalid request
        assert error.message == "Rate limit exceeded. Please try again later."
        error = cast("MCPErrorWithData", error)
        assert error.data["http_status"] == 429

    def test_init_with_retry_after(self) -> None:
        """Test initialization with retry_after."""
        error = TraktRateLimitError(retry_after=60)
        error = cast("MCPErrorWithData", error)
        assert error.message == "Rate limit exceeded. Please retry in 60 seconds."
        assert error.data["retry_after"] == 60

    def test_init_with_custom_message(self) -> None:
        """Test initialization with custom message."""
        error = TraktRateLimitError(retry_after=30, message="Custom rate limit message")
        error = cast("MCPErrorWithData", error)
        assert error.message == "Custom rate limit message"
        assert error.data["retry_after"] == 30

    def test_init_with_context(self) -> None:
        """Test initialization with context."""
        error = TraktRateLimitError(
            endpoint="/shows/trending", correlation_id="test-456"
        )
        error = cast("MCPErrorWithData", error)
        assert error.data["endpoint"] == "/shows/trending"
        assert error.data["correlation_id"] == "test-456"

    def test_inheritance(self) -> None:
        """Test proper inheritance chain."""
        error = TraktRateLimitError()

        assert isinstance(error, TraktAPIError)
        assert isinstance(error, MCPError)


class TestTraktServerError:
    """Test TraktServerError class."""

    def test_init_500_basic(self) -> None:
        """Test initialization with 500 status."""
        error = TraktServerError(500)
        error = cast("MCPErrorWithData", error)
        assert error.code == -32603  # Internal error
        assert error.message == "Trakt API server error (HTTP 500)"
        assert error.data["http_status"] == 500
        assert error.data["is_temporary"] is True

    def test_init_502_bad_gateway(self) -> None:
        """Test initialization with 502 status."""
        error = TraktServerError(502)
        error = cast("MCPErrorWithData", error)
        assert (
            error.message == "Bad gateway. The Trakt API server is experiencing issues."
        )
        assert error.data["http_status"] == 502

    def test_init_503_service_unavailable(self) -> None:
        """Test initialization with 503 status."""
        error = TraktServerError(503)
        error = cast("MCPErrorWithData", error)
        assert error.message == "Service unavailable. Please try again in 30 seconds."
        assert error.data["http_status"] == 503

    def test_init_with_custom_message(self) -> None:
        """Test initialization with custom message."""
        error = TraktServerError(500, message="Custom server error message")
        error = cast("MCPErrorWithData", error)
        assert error.message == "Custom server error message"
        assert error.data["http_status"] == 500

    def test_init_not_temporary(self) -> None:
        """Test initialization with permanent error flag."""
        error = TraktServerError(500, is_temporary=False)
        error = cast("MCPErrorWithData", error)
        assert error.data["is_temporary"] is False

    def test_init_with_context(self) -> None:
        """Test initialization with context."""
        error = TraktServerError(502, endpoint="/api/test", correlation_id="test-789")
        error = cast("MCPErrorWithData", error)
        assert error.data["endpoint"] == "/api/test"
        assert error.data["correlation_id"] == "test-789"

    def test_inheritance(self) -> None:
        """Test proper inheritance chain."""
        error = TraktServerError(500)
        error = cast("MCPErrorWithData", error)
        assert isinstance(error, TraktAPIError)
        assert isinstance(error, MCPError)


class TestErrorHierarchy:
    """Test error class inheritance and relationships."""

    def test_all_errors_inherit_from_mcp_error(self) -> None:
        """Test all custom errors inherit from MCPError."""
        errors = [
            TraktAPIError(-32600, "test"),
            AuthenticationRequiredError("test"),
            AuthorizationPendingError(),
            TraktValidationError("test"),
            TraktResourceNotFoundError("show", "test"),
            TraktRateLimitError(),
            TraktServerError(500),
        ]

        for error in errors:
            assert isinstance(error, MCPError)

    def test_error_serialization(self) -> None:
        """Test all errors can be serialized to dict."""
        errors = [
            TraktAPIError(-32600, "test"),
            AuthenticationRequiredError("test"),
            AuthorizationPendingError(),
            TraktValidationError("test"),
            TraktResourceNotFoundError("show", "test"),
            TraktRateLimitError(),
            TraktServerError(500),
        ]

        for error in errors:
            result = error.to_dict()
            assert "code" in result
            assert "message" in result
            assert isinstance(result["code"], int)
            assert isinstance(result["message"], str)

    def test_error_types_have_correct_codes(self) -> None:
        """Test error types have expected JSON-RPC codes."""
        # Test specific code expectations
        assert AuthenticationRequiredError("test").code == -32600
        assert AuthorizationPendingError().code == -32001
        assert TraktValidationError("test").code == -32602
        assert TraktResourceNotFoundError("show", "test").code == -32600
        assert TraktRateLimitError().code == -32600
        assert TraktServerError(500).code == -32603
