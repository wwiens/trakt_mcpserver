"""Split decorator implementation for perfect type inference."""

import functools
from collections.abc import Awaitable, Callable
from typing import Any, Concatenate, ParamSpec, TypeVar

import httpx

# Set up structured logging
from .structured_logging import get_structured_logger

logger = get_structured_logger("trakt_mcp")

# Standard MCP error codes (JSON-RPC 2.0)
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# Type variables
P = ParamSpec("P")
R = TypeVar("R")
Self = TypeVar("Self")


class MCPError(Exception):
    """Base MCP-compliant error following JSON-RPC 2.0 specification."""

    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        """Initialize MCP error.

        Args:
            code: Standard JSON-RPC error code
            message: Human-readable error message
            data: Optional additional error data
        """
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary format for JSON-RPC response."""
        error_dict = {"code": self.code, "message": self.message}
        if self.data is not None:
            error_dict["data"] = self.data
        return error_dict


class InvalidParamsError(MCPError):
    """Invalid parameters error (-32602)."""

    def __init__(self, message: str, data: Any | None = None) -> None:
        super().__init__(INVALID_PARAMS, message, data)


class InternalError(MCPError):
    """Internal server error (-32603)."""

    def __init__(self, message: str, data: Any | None = None) -> None:
        super().__init__(INTERNAL_ERROR, message, data)


class InvalidRequestError(MCPError):
    """Invalid request error (-32600)."""

    def __init__(self, message: str, data: Any | None = None) -> None:
        super().__init__(INVALID_REQUEST, message, data)


def handle_api_errors(
    method: Callable[Concatenate[Any, ...], Awaitable[Any]],
) -> Callable[Concatenate[Any, ...], Awaitable[Any]]:
    """Handle API errors for class methods with perfect type inference.

    This decorator is specifically designed for methods (functions with self/cls parameter).
    For standalone functions, use @handle_api_errors_func instead.

    Args:
        method: The async method to wrap

    Returns:
        Wrapped method that handles API errors using MCP error format
    """

    @functools.wraps(method)
    async def wrapper(self: Any, /, *args: Any, **kwargs: Any) -> Any:
        # Import here to avoid circular imports
        from .error_handler import TraktAPIErrorHandler
        from .request_context import add_context_to_error_data, get_current_context

        # Get current request context
        context = get_current_context()
        correlation_id = context.correlation_id if context else None

        try:
            result = await method(self, *args, **kwargs)
            return result
        except httpx.HTTPStatusError as e:
            # Use centralized error handler with enhanced context
            error = TraktAPIErrorHandler.handle_http_error(
                error=e,
                endpoint=context.endpoint if context else None,
                resource_type=context.resource_type if context else None,
                correlation_id=correlation_id,
            )
            # Add full request context to error data
            if context:
                error.data = add_context_to_error_data(error.data or {})
            raise error from e
        except httpx.RequestError as e:
            # Create base error data with context
            error_data = {
                "error_type": "request_error",
                "details": str(e),
            }
            if context:
                error_data = add_context_to_error_data(error_data)
            else:
                if correlation_id is not None:
                    error_data["correlation_id"] = correlation_id

            logger.error(
                f"Request error: {e!s}",
                extra=error_data,
            )
            raise InternalError(
                "Unable to connect to Trakt API. Please check your internet connection.",
                data=error_data,
            ) from e
        except MCPError:
            # Re-raise MCP errors as-is
            raise
        except (ValueError, TypeError, KeyError, AttributeError):
            # Re-raise business logic errors as-is
            raise
        except Exception as e:
            # Create base error data with context
            error_data = {
                "error_type": "unexpected_error",
            }
            if context:
                error_data = add_context_to_error_data(error_data)
            else:
                if correlation_id is not None:
                    error_data["correlation_id"] = correlation_id

            logger.exception(
                "Unexpected error",
                extra=error_data,
            )
            raise InternalError(
                f"An unexpected error occurred: {e!s}",
                data=error_data,
            ) from e

    return wrapper


def handle_api_errors_func(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """Handle API errors for standalone functions with perfect type inference.

    This decorator is specifically designed for standalone functions (no self/cls parameter).
    For class methods, use @handle_api_errors instead.

    Args:
        func: The async function to wrap

    Returns:
        Wrapped function that handles API errors using MCP error format
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Import here to avoid circular imports
        from .error_handler import TraktAPIErrorHandler
        from .request_context import add_context_to_error_data, get_current_context

        # Get current request context
        context = get_current_context()
        correlation_id = context.correlation_id if context else None

        try:
            result = await func(*args, **kwargs)
            return result
        except httpx.HTTPStatusError as e:
            # Use centralized error handler with enhanced context
            error = TraktAPIErrorHandler.handle_http_error(
                error=e,
                endpoint=context.endpoint if context else None,
                resource_type=context.resource_type if context else None,
                correlation_id=correlation_id,
            )
            # Add full request context to error data
            if context:
                error.data = add_context_to_error_data(error.data or {})
            raise error from e
        except httpx.RequestError as e:
            # Create base error data with context
            error_data = {
                "error_type": "request_error",
                "details": str(e),
            }
            if context:
                error_data = add_context_to_error_data(error_data)
            else:
                if correlation_id is not None:
                    error_data["correlation_id"] = correlation_id

            logger.error(
                f"Request error: {e!s}",
                extra=error_data,
            )
            raise InternalError(
                "Unable to connect to Trakt API. Please check your internet connection.",
                data=error_data,
            ) from e
        except MCPError:
            # Re-raise MCP errors as-is
            raise
        except (ValueError, TypeError, KeyError, AttributeError):
            # Re-raise business logic errors as-is
            raise
        except Exception as e:
            # Create base error data with context
            error_data = {
                "error_type": "unexpected_error",
            }
            if context:
                error_data = add_context_to_error_data(error_data)
            else:
                if correlation_id is not None:
                    error_data["correlation_id"] = correlation_id

            logger.exception(
                "Unexpected error",
                extra=error_data,
            )
            raise InternalError(
                f"An unexpected error occurred: {e!s}",
                data=error_data,
            ) from e

    return wrapper


__all__ = [
    "InternalError",
    "InvalidParamsError",
    "InvalidRequestError",
    "MCPError",
    "handle_api_errors",
    "handle_api_errors_func",
]
