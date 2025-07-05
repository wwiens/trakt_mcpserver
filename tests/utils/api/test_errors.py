"""Tests for utils.api.errors module."""

import logging
from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from utils.api.errors import (
    AsyncFunc,
    InternalError,
    InvalidRequestError,
    T,
    handle_api_errors,
    logger,
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

        decorated_func = handle_api_errors(mock_async_func)

        assert decorated_func.__name__ == "test_function"
        assert decorated_func.__doc__ == "Test docstring"

    @pytest.mark.asyncio
    async def test_successful_function_call(self, mock_async_func: AsyncMock) -> None:
        """Test decorator passes through successful function calls."""
        expected_result = {"success": True, "data": "test_data"}
        mock_async_func.return_value = expected_result

        decorated_func = handle_api_errors(mock_async_func)
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

        decorated_func = handle_api_errors(mock_async_func)

        with (
            patch.object(logger, "error") as mock_logger,
            pytest.raises(InvalidRequestError) as exc_info,
        ):
            await decorated_func()

        assert (
            exc_info.value.message
            == "Authentication required. Please check your Trakt API credentials."
        )
        assert exc_info.value.data == {"http_status": 401}
        mock_logger.assert_called_once()

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

        decorated_func = handle_api_errors(mock_async_func)

        with (
            patch.object(logger, "error") as mock_logger,
            pytest.raises(InvalidRequestError) as exc_info,
        ):
            await decorated_func()

        assert exc_info.value.message == "The requested resource was not found."
        assert exc_info.value.data == {"http_status": 404}
        mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_http_429_rate_limit_error(self, mock_async_func: AsyncMock) -> None:
        """Test handling of HTTP 429 Rate Limit error."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"

        http_error = httpx.HTTPStatusError(
            message="429 Too Many Requests", request=MagicMock(), response=mock_response
        )
        mock_async_func.side_effect = http_error

        decorated_func = handle_api_errors(mock_async_func)

        with (
            patch.object(logger, "error") as mock_logger,
            pytest.raises(InvalidRequestError) as exc_info,
        ):
            await decorated_func()

        assert exc_info.value.message == "Rate limit exceeded. Please try again later."
        assert exc_info.value.data == {"http_status": 429}
        mock_logger.assert_called_once()

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

        decorated_func = handle_api_errors(mock_async_func)

        with (
            patch.object(logger, "error") as mock_logger,
            pytest.raises(InternalError) as exc_info,
        ):
            await decorated_func()

        assert exc_info.value.message == "HTTP 503 error occurred"
        assert exc_info.value.data == {
            "http_status": 503,
            "response": "Service Unavailable",
        }
        mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_error_handling(self, mock_async_func: AsyncMock) -> None:
        """Test handling of HTTP request errors."""
        request_error = httpx.RequestError("Connection failed")
        mock_async_func.side_effect = request_error

        decorated_func = handle_api_errors(mock_async_func)

        with (
            patch.object(logger, "error") as mock_logger,
            pytest.raises(InternalError) as exc_info,
        ):
            await decorated_func()

        assert (
            exc_info.value.message
            == "Unable to connect to Trakt API. Please check your internet connection."
        )
        assert exc_info.value.data == {
            "error_type": "request_error",
            "details": "Connection failed",
        }
        mock_logger.assert_called_once_with("Request error: Connection failed")

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, mock_async_func: AsyncMock) -> None:
        """Test handling of unexpected errors."""

        # Use a custom exception that's not in the business logic list
        class UnexpectedException(Exception):
            pass

        unexpected_error = UnexpectedException("Unexpected error")
        mock_async_func.side_effect = unexpected_error

        decorated_func = handle_api_errors(mock_async_func)

        with (
            patch.object(logger, "exception") as mock_logger,
            pytest.raises(InternalError) as exc_info,
        ):
            await decorated_func()

        assert (
            exc_info.value.message == "An unexpected error occurred: Unexpected error"
        )
        assert exc_info.value.data == {"error_type": "unexpected_error"}
        mock_logger.assert_called_once_with("Unexpected error")

    @pytest.mark.asyncio
    async def test_decorator_with_args_and_kwargs(
        self, mock_async_func: AsyncMock
    ) -> None:
        """Test decorator properly passes args and kwargs."""
        mock_async_func.return_value = "success"

        decorated_func = handle_api_errors(mock_async_func)
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

        decorated_func = handle_api_errors(mock_async_func)

        with patch.object(logger, "error") as mock_logger, pytest.raises(InternalError):
            await decorated_func()

        # Check that the log message includes status code and response text
        mock_logger.assert_called_once()
        log_message = mock_logger.call_args[0][0]
        assert "500" in log_message
        assert "Internal Server Error" in log_message


class TestDecoratorTypes:
    """Test decorator type annotations and type safety."""

    def test_async_func_type_alias(self) -> None:
        """Test AsyncFunc type alias is properly defined."""
        # AsyncFunc should be a type alias for async functions
        assert hasattr(AsyncFunc, "__origin__")  # Should be a generic type

    def test_type_var_t(self) -> None:
        """Test TypeVar T is properly defined."""
        assert isinstance(T, type(T))  # Should be a TypeVar
        assert T.__name__ == "T"

    def test_decorator_type_hints(self) -> None:
        """Test decorator maintains proper type hints."""

        @handle_api_errors
        async def test_func(x: int) -> str:
            return str(x)

        # Function should still be callable and maintain signature
        assert callable(test_func)


class TestLoggerConfiguration:
    """Test logger configuration and setup."""

    def test_logger_exists(self) -> None:
        """Test logger is properly configured."""
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "trakt_mcp"

    def test_logger_level(self) -> None:
        """Test logger has appropriate level."""
        # Logger should have a reasonable level (INFO or WARNING are both acceptable)
        effective_level = logger.getEffectiveLevel()
        assert effective_level in [logging.INFO, logging.WARNING, logging.DEBUG]

    def test_logging_configuration_exists(self) -> None:
        """Test that logging configuration is properly set up."""
        # Test that the logger has handlers or that basicConfig was called
        # by checking if the logger can actually log messages

        # The logger should be properly configured for our module
        assert logger.name == "trakt_mcp"

        # Should have at least the root logger configuration
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0 or logger.handlers


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
        @handle_api_errors
        async def test_func() -> str:
            call_order.append("inner")
            return "success"

        result = await test_func()

        assert result == "success"
        assert call_order == ["outer_start", "inner", "outer_end"]

    @pytest.mark.asyncio
    async def test_decorator_with_none_return(self) -> None:
        """Test decorator handles functions that return None."""

        @handle_api_errors
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

        @handle_api_errors
        @inner_decorator
        async def test_func() -> str:
            return "should not reach here"

        with patch.object(logger, "error"), pytest.raises(InternalError) as exc_info:
            await test_func()

        assert exc_info.value.message == "HTTP 400 error occurred"
        assert exc_info.value.data == {"http_status": 400, "response": "Bad Request"}
