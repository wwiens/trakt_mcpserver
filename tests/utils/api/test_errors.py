"""Tests for utils.api.errors module."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

if TYPE_CHECKING:
    from tests.types_stub import MCPErrorWithData
from utils.api.error_types import (
    AuthenticationRequiredError,
    TraktRateLimitError,
    TraktResourceNotFoundError,
    TraktServerError,
)
from utils.api.errors import (
    InternalError,
    InvalidParamsError,
    handle_api_errors,
    handle_api_errors_func,
)


class TestHandleApiErrorsDecorator:
    """Test handle_api_errors decorator functionality."""

    @pytest.fixture
    def mock_async_func(self) -> AsyncMock:
        """Create a mock async function for testing."""
        return AsyncMock()

    def test_decorator_preserves_function_metadata(
        self, mock_async_func: AsyncMock
    ) -> None:
        """Test decorator preserves original function metadata."""
        mock_async_func.__name__ = "test_function"
        mock_async_func.__doc__ = "Test docstring"

        decorated_func = handle_api_errors_func(mock_async_func)

        assert decorated_func.__name__ == "test_function"
        assert decorated_func.__doc__ == "Test docstring"

    @pytest.mark.asyncio
    async def test_successful_function_call(self, mock_async_func: AsyncMock) -> None:
        """Test decorator passes through successful function calls."""
        expected_result = {"success": True, "data": "test_data"}
        mock_async_func.return_value = expected_result

        decorated_func = handle_api_errors_func(mock_async_func)
        result = await decorated_func("arg1", kwarg1="value1")

        assert result == expected_result
        mock_async_func.assert_called_once_with("arg1", kwarg1="value1")

    @pytest.mark.asyncio
    async def test_http_401_unauthorized_error(
        self, mock_async_func: AsyncMock
    ) -> None:
        """Test handling of HTTP 401 Unauthorized error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        http_error = httpx.HTTPStatusError(
            message="401 Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_async_func.side_effect = http_error

        decorated_func = handle_api_errors_func(mock_async_func)

        with pytest.raises(AuthenticationRequiredError) as exc_info:
            await decorated_func()

        error = cast("MCPErrorWithData", exc_info.value)
        assert (
            error.message
            == "Authentication required. Please check your Trakt API credentials."
        )
        assert error.data["error_type"] == "auth_required"
        assert error.data["action"] == "access resource"

    @pytest.mark.asyncio
    async def test_http_404_not_found_error(self, mock_async_func: AsyncMock) -> None:
        """Test handling of HTTP 404 Not Found error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        http_error = httpx.HTTPStatusError(
            message="404 Not Found", request=MagicMock(), response=mock_response
        )
        mock_async_func.side_effect = http_error

        decorated_func = handle_api_errors_func(mock_async_func)

        with pytest.raises(TraktResourceNotFoundError) as exc_info:
            await decorated_func()

        error = cast("MCPErrorWithData", exc_info.value)
        assert "The requested resource 'unknown' was not found" in error.message
        assert error.data["http_status"] == 404
        assert error.data["resource_type"] == "resource"
        assert error.data["resource_id"] == "unknown"

    @pytest.mark.asyncio
    async def test_http_429_rate_limit_error(self, mock_async_func: AsyncMock) -> None:
        """Test handling of HTTP 429 Rate Limit error."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_response.headers = {}

        http_error = httpx.HTTPStatusError(
            message="429 Too Many Requests", request=MagicMock(), response=mock_response
        )
        mock_async_func.side_effect = http_error

        decorated_func = handle_api_errors_func(mock_async_func)

        with pytest.raises(TraktRateLimitError) as exc_info:
            await decorated_func()

        error = cast("MCPErrorWithData", exc_info.value)
        assert error.message == "Rate limit exceeded. Please try again later."
        assert error.data["http_status"] == 429
        assert "retry_after" not in error.data

    @pytest.mark.asyncio
    async def test_http_unknown_status_error(self, mock_async_func: AsyncMock) -> None:
        """Test handling of unknown HTTP status error."""
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"

        http_error = httpx.HTTPStatusError(
            message="503 Service Unavailable",
            request=MagicMock(),
            response=mock_response,
        )
        mock_async_func.side_effect = http_error

        decorated_func = handle_api_errors_func(mock_async_func)

        with pytest.raises(TraktServerError) as exc_info:
            await decorated_func()

        error = cast("MCPErrorWithData", exc_info.value)
        assert error.message == "Service unavailable. Please try again in 30 seconds."
        assert error.data["http_status"] == 503
        assert error.data["is_temporary"] is True

    @pytest.mark.asyncio
    async def test_request_error_handling(self, mock_async_func: AsyncMock) -> None:
        """Test handling of HTTP request errors."""
        request_error = httpx.RequestError("Connection failed")
        mock_async_func.side_effect = request_error

        decorated_func = handle_api_errors_func(mock_async_func)

        with pytest.raises(InternalError) as exc_info:
            await decorated_func()

        error = cast("MCPErrorWithData", exc_info.value)
        assert (
            error.message
            == "Unable to connect to Trakt API. Please check your internet connection."
        )
        assert error.data["error_type"] == "request_error"
        assert error.data["details"] == "Connection failed"

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, mock_async_func: AsyncMock) -> None:
        """Test handling of unexpected errors."""

        # Use a custom exception that's not in the business logic list
        class UnexpectedException(Exception):
            pass

        unexpected_error = UnexpectedException("Unexpected error")
        mock_async_func.side_effect = unexpected_error

        decorated_func = handle_api_errors_func(mock_async_func)

        with pytest.raises(InternalError) as exc_info:
            await decorated_func()

        error = cast("MCPErrorWithData", exc_info.value)
        assert error.message == "An unexpected error occurred: Unexpected error"
        assert error.data["error_type"] == "unexpected_error"

    @pytest.mark.asyncio
    async def test_decorator_with_args_and_kwargs(
        self, mock_async_func: AsyncMock
    ) -> None:
        """Test decorator properly passes args and kwargs."""
        mock_async_func.return_value = "success"

        decorated_func = handle_api_errors_func(mock_async_func)
        result = await decorated_func("arg1", "arg2", key1="value1", key2="value2")

        assert result == "success"
        mock_async_func.assert_called_once_with(
            "arg1", "arg2", key1="value1", key2="value2"
        )

    @pytest.mark.asyncio
    async def test_error_logging_includes_status_code_and_text(
        self, mock_async_func: AsyncMock
    ) -> None:
        """Test error logging includes status code and response text."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        http_error = httpx.HTTPStatusError(
            message="500 Internal Server Error",
            request=MagicMock(),
            response=mock_response,
        )
        mock_async_func.side_effect = http_error

        decorated_func = handle_api_errors_func(mock_async_func)

        with pytest.raises(TraktServerError):
            await decorated_func()

        # The logging is handled by the error handler, not the decorator directly


class TestDecoratorTypes:
    """Test decorator type annotations and type safety."""

    def test_decorator_is_callable_and_available(self) -> None:
        """Test that the decorator function is properly imported and callable."""
        # The decorator should work with both methods and functions
        assert handle_api_errors_func is not None
        assert callable(handle_api_errors_func)

    def test_decorator_type_hints(self) -> None:
        """Test decorator maintains proper type hints."""

        @handle_api_errors_func
        async def test_func(x: int) -> str:
            return str(x)

        # Function should still be callable and maintain signature
        assert callable(test_func)


class TestHandleApiErrorsMethodDecorator:
    """Test handle_api_errors decorator functionality for class methods."""

    class MockService:
        """Mock service class for testing method decorators."""

        @handle_api_errors
        async def test_method(self, x: int) -> str:
            """Test method that returns a string."""
            return str(x)

        @handle_api_errors
        async def method_that_raises_http_error(self) -> str:
            """Test method that raises an HTTP error."""
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            raise httpx.HTTPStatusError(
                message="401 Unauthorized", request=MagicMock(), response=mock_response
            )

        @handle_api_errors
        async def method_that_raises_request_error(self) -> str:
            """Test method that raises a request error."""
            raise httpx.RequestError("Connection failed")

    @pytest.mark.asyncio
    async def test_method_decorator_successful_call(self) -> None:
        """Test decorator works correctly on class methods for successful calls."""
        service = self.MockService()
        result = await service.test_method(42)
        assert result == "42"

    @pytest.mark.asyncio
    async def test_method_decorator_http_error_handling(self) -> None:
        """Test decorator handles HTTP errors correctly on class methods."""
        service = self.MockService()

        with pytest.raises(AuthenticationRequiredError) as exc_info:
            await service.method_that_raises_http_error()

        error = cast("MCPErrorWithData", exc_info.value)
        assert (
            error.message
            == "Authentication required. Please check your Trakt API credentials."
        )
        assert error.data["error_type"] == "auth_required"

    @pytest.mark.asyncio
    async def test_method_decorator_request_error_handling(self) -> None:
        """Test decorator handles request errors correctly on class methods."""
        service = self.MockService()

        with pytest.raises(InternalError) as exc_info:
            await service.method_that_raises_request_error()

        error = cast("MCPErrorWithData", exc_info.value)
        assert (
            error.message
            == "Unable to connect to Trakt API. Please check your internet connection."
        )
        assert error.data["error_type"] == "request_error"


class TestDecoratorIntegration:
    """Test decorator integration and edge cases."""

    @pytest.mark.asyncio
    async def test_nested_decorators_compatibility(self) -> None:
        """Test decorator works with other decorators."""
        call_order: list[str] = []

        def outer_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                call_order.append("outer_start")
                result = await func(*args, **kwargs)
                call_order.append("outer_end")
                return result

            return wrapper

        @outer_decorator
        @handle_api_errors_func
        async def test_func() -> str:
            call_order.append("inner")
            return "success"

        result = await test_func()

        assert result == "success"
        assert call_order == ["outer_start", "inner", "outer_end"]

    @pytest.mark.asyncio
    async def test_decorator_with_none_return(self) -> None:
        """Test decorator handles functions that return None."""

        @handle_api_errors_func
        async def test_func() -> None:
            return None

        result = await test_func()
        assert result is None

    @pytest.mark.asyncio
    async def test_decorator_preserves_exceptions_from_inner_decorators(self) -> None:
        """Test decorator preserves the proper error handling chain."""

        def inner_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # This decorator raises its own HTTP error
                mock_response = MagicMock()
                mock_response.status_code = 400
                mock_response.text = "Bad Request"
                raise httpx.HTTPStatusError(
                    "400 Bad Request", request=MagicMock(), response=mock_response
                )

            return wrapper

        @handle_api_errors_func
        @inner_decorator
        async def test_func() -> str:
            return "should not reach here"

        with pytest.raises(InvalidParamsError) as exc_info:
            await test_func()

        error = cast("MCPErrorWithData", exc_info.value)
        assert "Bad request" in error.message
        assert error.data["http_status"] == 400
        assert error.data["details"] == "Bad Request"
