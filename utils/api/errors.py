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


@runtime_checkable
class RefreshableAuthClient(ClearableAuthClient, Protocol):
    """Protocol for clients that support token refresh on 401."""

    async def refresh_access_token(self) -> bool:
        """Refresh the access token using the stored refresh token.

        Returns:
            True if refresh succeeded, False if refresh failed.
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


def _has_refresh_token(client: object) -> bool:
    """Check if the client has a refresh token available for recovery."""
    auth_token = getattr(client, "auth_token", None)
    if auth_token is None:
        return False
    return bool(getattr(auth_token, "refresh_token", None))


def _is_auth_required_error(error: MCPError) -> bool:
    """Check if an MCPError originated from a 401 HTTP status."""
    from .error_types import AuthenticationRequiredError

    return isinstance(error, AuthenticationRequiredError)


async def _execute_method_with_error_handling(
    method: Callable[..., Awaitable[Any]],
    self_obj: Any,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Execute a client method with standard error handling.

    Shared implementation for the first attempt and the retry after refresh.

    Args:
        method: The async method to call
        self_obj: The client instance (self)
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Result from the method call

    Raises:
        MCPError: On API or internal errors
    """
    from .error_handler import TraktAPIErrorHandler
    from .request_context import add_context_to_error_data, get_current_context

    context = get_current_context()
    correlation_id = context.correlation_id if context else None

    try:
        return await method(self_obj, *args, **kwargs)
    except httpx.HTTPStatusError as e:
        error = TraktAPIErrorHandler.handle_http_error(
            error=e,
            endpoint=context.endpoint if context else None,
            resource_type=context.resource_type if context else None,
            correlation_id=correlation_id,
        )
        if context:
            error.data = add_context_to_error_data(error.data or {})
        raise error from e
    except httpx.RequestError as e:
        error_data: dict[str, Any] = {
            "error_type": "request_error",
            "details": str(e),
        }
        if context:
            error_data = add_context_to_error_data(error_data)
        elif correlation_id is not None:
            error_data["correlation_id"] = correlation_id

        logger.error(f"Request error: {e!s}", extra=error_data)
        raise InternalError(
            "Unable to connect to Trakt API. Please check your internet connection.",
            data=error_data,
        ) from e
    except MCPError:
        raise
    except json.JSONDecodeError as e:
        error_data = {
            "error_type": "json_decode_error",
            "details": str(e),
        }
        if context:
            error_data = add_context_to_error_data(error_data)
        elif correlation_id is not None:
            error_data["correlation_id"] = correlation_id

        logger.error(f"JSON decode error: {e!s}", extra=error_data)
        raise InternalError(
            f"Invalid response format from API: {e!s}",
            data=error_data,
        ) from e
    except (ValueError, TypeError, KeyError, AttributeError):
        raise
    except Exception as e:
        error_data = {"error_type": "unexpected_error"}
        if context:
            error_data = add_context_to_error_data(error_data)
        elif correlation_id is not None:
            error_data["correlation_id"] = correlation_id

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

    On 401 Unauthorized, attempts to refresh the access token (if the client
    supports it) and retries the call once before clearing the token and raising.

    Args:
        method: The async method to wrap

    Returns:
        Wrapped method that handles API errors using MCP error format
    """

    @functools.wraps(method)
    async def wrapper(self: Any, /, *args: Any, **kwargs: Any) -> Any:
        try:
            # First attempt — do NOT clear token on 401 so refresh can recover
            return await _execute_method_with_error_handling(method, self, args, kwargs)
        except MCPError as first_error:
            if not _is_auth_required_error(first_error):
                raise

            # 401 path — attempt refresh if client supports it.
            # Guard against recursive refresh: if _refresh_lock is held,
            # we're already inside refresh_access_token's HTTP call chain.
            refresh_lock = getattr(self, "_refresh_lock", None)
            already_refreshing = refresh_lock is not None and refresh_lock.locked()

            if (
                not already_refreshing
                and isinstance(self, RefreshableAuthClient)
                and _has_refresh_token(self)
            ):
                try:
                    refreshed = await self.refresh_access_token()
                except Exception:
                    logger.warning(
                        "Token refresh failed during 401 recovery", exc_info=True
                    )
                    refreshed = False

                if refreshed:
                    try:
                        # Retry once with refreshed token
                        return await _execute_method_with_error_handling(
                            method, self, args, kwargs
                        )
                    except MCPError:
                        # Retry also failed — clear and raise the retry error
                        _auto_clear_invalid_token(self)
                        raise

            # No refresh possible or refresh failed — clear and raise original
            _auto_clear_invalid_token(self)
            raise

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
                "Unable to connect to Trakt API. "
                + "Please check your internet connection.",
                data=error_data,
            ) from e
        except MCPError as e:
            # Server-layer decorator: convert auth errors to friendly messages
            # so MCP clients see helpful text instead of raw error payloads.
            # (The class-method decorator handle_api_errors re-raises MCPErrors
            # so the server layer can handle them with full request context.)
            from .error_types import (
                AuthenticationRequiredError,
                extract_auth_action,
                format_auth_required_message,
            )

            if isinstance(e, AuthenticationRequiredError):
                return format_auth_required_message(extract_auth_action(e))
            # Re-raise other MCP errors as-is
            raise
        except json.JSONDecodeError as e:
            # Treat JSON decode errors as internal errors
            error_data = {
                "error_type": "json_decode_error",
                "details": str(e),
            }
            if context:
                error_data = add_context_to_error_data(error_data)
            else:
                if correlation_id is not None:
                    error_data["correlation_id"] = correlation_id

            logger.error(
                f"JSON decode error: {e!s}",
                extra=error_data,
            )
            raise InternalError(
                f"Invalid response format from API: {e!s}",
                data=error_data,
            ) from e
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
    "ClearableAuthClient",
    "InternalError",
    "InvalidParamsError",
    "InvalidRequestError",
    "MCPError",
    "RefreshableAuthClient",
    "handle_api_errors",
    "handle_api_errors_func",
]
