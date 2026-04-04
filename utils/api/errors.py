"""Split decorator implementation for perfect type inference."""

import functools
import json
from collections.abc import Awaitable, Callable
from typing import (
    Any,
    Concatenate,
    Final,
    ParamSpec,
    Protocol,
    TypeVar,
    runtime_checkable,
)

import httpx

from .request_context import RequestContext

# Set up structured logging
from .structured_logging import get_structured_logger

logger = get_structured_logger("trakt_mcp")

# Standard MCP error codes (JSON-RPC 2.0)
PARSE_ERROR: Final[int] = -32700
INVALID_REQUEST: Final[int] = -32600
METHOD_NOT_FOUND: Final[int] = -32601
INVALID_PARAMS: Final[int] = -32602
INTERNAL_ERROR: Final[int] = -32603

# Type variables
P = ParamSpec("P")
R = TypeVar("R")
Self = TypeVar("Self")


@runtime_checkable
class ClearableAuthClient(Protocol):
    """Protocol for clients that support clearing authentication tokens."""

    def clear_auth_token(self) -> bool:
        """Clear the stored authentication token.

        Returns:
            True if token was cleared, False if no token existed or already cleared.
        """
        ...


def _auto_clear_invalid_token(client: ClearableAuthClient | object) -> None:
    """Clear invalid auth token from client if it has one.

    Called when API returns 401 Unauthorized, indicating the saved
    token is invalid, expired, or revoked. Clears the token to allow
    fresh authentication.

    Args:
        client: Client instance that may have a clear_auth_token method
    """
    if isinstance(client, ClearableAuthClient):
        try:
            cleared = client.clear_auth_token()
            if cleared:
                logger.info(
                    "Auto-cleared invalid authentication token after 401 response"
                )
            else:
                logger.debug("Token already cleared or absent after 401 response")
        except OSError:
            logger.warning("Failed to auto-clear invalid token", exc_info=True)


class MCPError(Exception):
    """Base MCP-compliant error following JSON-RPC 2.0 specification."""

    def __init__(
        self, code: int, message: str, data: dict[str, Any] | None = None
    ) -> None:
        """Initialize MCP error.

        Args:
            code: Standard JSON-RPC error code
            message: Human-readable error message
            data: Optional additional error data dictionary
        """
        self.code = code
        self.message = message
        self.data: dict[str, Any] | None = data
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary format for JSON-RPC response."""
        error_dict: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data is not None:
            error_dict["data"] = self.data
        return error_dict


class InvalidParamsError(MCPError):
    """Invalid parameters error (-32602)."""

    def __init__(self, message: str, data: dict[str, Any] | None = None) -> None:
        super().__init__(INVALID_PARAMS, message, data)


class InternalError(MCPError):
    """Internal server error (-32603)."""

    def __init__(self, message: str, data: dict[str, Any] | None = None) -> None:
        super().__init__(INTERNAL_ERROR, message, data)


class InvalidRequestError(MCPError):
    """Invalid request error (-32600)."""

    def __init__(self, message: str, data: dict[str, Any] | None = None) -> None:
        super().__init__(INVALID_REQUEST, message, data)


def _build_error_data(
    error_type: str,
    context: RequestContext | None,
    correlation_id: str | None,
    *,
    details: str | None = None,
) -> dict[str, Any]:
    """Build error data dict with optional request context.

    Args:
        error_type: Error classification string
        context: Current request context (or None)
        correlation_id: Optional correlation ID
        details: Optional error details string

    Returns:
        Error data dictionary with context information
    """
    from .request_context import add_context_to_error_data

    error_data: dict[str, Any] = {"error_type": error_type}
    if details is not None:
        error_data["details"] = details
    if context:
        error_data = add_context_to_error_data(error_data)
    elif correlation_id is not None:
        error_data["correlation_id"] = correlation_id
    return error_data


async def _execute_with_error_handling(
    coro: Awaitable[R],
    *,
    on_401: Callable[[], None] | None = None,
    convert_auth_errors: bool = False,
) -> R | str:
    """Execute an awaitable with shared error handling logic.

    Args:
        coro: The awaitable to execute
        on_401: Optional callback to invoke on 401 HTTP status (e.g., clear auth token)
        convert_auth_errors: If True, convert AuthenticationRequiredError to
            friendly messages instead of re-raising

    Returns:
        The awaited result of type R on success. When convert_auth_errors is True
        and an AuthenticationRequiredError is caught, returns a formatted str
        message (via format_auth_required_message) instead of re-raising.

    Raises:
        MCPError: On API or internal errors
        ValueError, TypeError, KeyError, AttributeError: Re-raised as-is
    """
    from .error_handler import TraktAPIErrorHandler
    from .request_context import add_context_to_error_data, get_current_context

    context = get_current_context()
    correlation_id = context.correlation_id if context else None

    try:
        return await coro
    except httpx.HTTPStatusError as e:
        error = TraktAPIErrorHandler.handle_http_error(
            error=e,
            endpoint=context.endpoint if context else None,
            resource_type=context.resource_type if context else None,
            correlation_id=correlation_id,
        )
        if context:
            error.data = add_context_to_error_data(error.data or {})

        if on_401 is not None and e.response.status_code == 401:
            try:
                on_401()
            except Exception:
                logger.warning("on_401 callback failed", exc_info=True)

        raise error from e
    except httpx.RequestError as e:
        error_data = _build_error_data(
            "request_error", context, correlation_id, details=str(e)
        )
        logger.error(f"Request error: {e!s}", extra=error_data)
        raise InternalError(
            "Unable to connect to Trakt API. Please check your internet connection.",
            data=error_data,
        ) from e
    except MCPError as e:
        if convert_auth_errors:
            from .error_types import (
                AuthenticationRequiredError,
                extract_auth_action,
                format_auth_required_message,
            )

            if isinstance(e, AuthenticationRequiredError):
                return format_auth_required_message(extract_auth_action(e))
        raise
    except json.JSONDecodeError as e:
        error_data = _build_error_data(
            "json_decode_error", context, correlation_id, details=str(e)
        )
        logger.error(f"JSON decode error: {e!s}", extra=error_data)
        raise InternalError(
            f"Invalid response format from API: {e!s}",
            data=error_data,
        ) from e
    except (ValueError, TypeError, KeyError, AttributeError):
        raise
    except Exception as e:
        error_data = _build_error_data("unexpected_error", context, correlation_id)
        logger.exception("Unexpected error", extra=error_data)
        raise InternalError(
            f"An unexpected error occurred: {e!s}",
            data=error_data,
        ) from e


def handle_api_errors(
    method: Callable[Concatenate[Any, ...], Awaitable[Any]],
) -> Callable[Concatenate[Any, ...], Awaitable[Any]]:
    """Handle API errors for class methods with perfect type inference.

    This decorator is specifically designed for methods (functions with
    self/cls parameter). For standalone functions, use @handle_api_errors_func
    instead.

    Args:
        method: The async method to wrap

    Returns:
        Wrapped method that handles API errors using MCP error format
    """

    @functools.wraps(method)
    async def wrapper(self: Any, /, *args: Any, **kwargs: Any) -> Any:
        return await _execute_with_error_handling(
            method(self, *args, **kwargs),
            on_401=lambda: _auto_clear_invalid_token(self),
        )

    return wrapper


def handle_api_errors_func(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """Handle API errors for standalone functions with perfect type inference.

    This decorator is specifically designed for standalone functions
    (no self/cls parameter). For class methods, use @handle_api_errors instead.

    Note: Unlike @handle_api_errors, this decorator does NOT auto-clear authentication
    tokens on 401 responses because standalone functions don't have access to a client
    instance. Server tools that need token clearing should handle this explicitly.

    Args:
        func: The async function to wrap

    Returns:
        Wrapped function that handles API errors using MCP error format
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await _execute_with_error_handling(
            func(*args, **kwargs),
            convert_auth_errors=True,
        )

    return wrapper


__all__ = [
    "ClearableAuthClient",
    "InternalError",
    "InvalidParamsError",
    "InvalidRequestError",
    "MCPError",
    "handle_api_errors",
    "handle_api_errors_func",
]
