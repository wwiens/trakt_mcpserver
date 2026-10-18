"""Split decorator implementation for perfect type inference."""

import functools
import json
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import (
    Any,
    Concatenate,
    Final,
    Protocol,
    runtime_checkable,
)

import httpx

from utils.api.hosts import is_auth_host_url

from .request_context import RequestContext

# Set up structured logging
from .structured_logging import get_structured_logger

logger = get_structured_logger("trakt_mcp")

# Standard MCP error codes (JSON-RPC 2.0)
INVALID_REQUEST: Final[int] = -32600
INVALID_PARAMS: Final[int] = -32602
INTERNAL_ERROR: Final[int] = -32603


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

    async def refresh_access_token(
        self, rejected_access_token: str | None = None
    ) -> bool:
        """Refresh the access token using the stored refresh token.

        Args:
            rejected_access_token: Access token the server just answered with
                401; refresh even if it still looks unexpired locally.

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
        # Set once a 401 recovery has run, so outer @handle_api_errors layers
        # re-raise instead of spending the single-use refresh token again.
        self.refresh_attempted: bool = False
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


def _http_status_error(error: MCPError) -> httpx.HTTPStatusError | None:
    """Return the HTTP error an MCPError was raised from, if any."""
    cause = error.__cause__
    return cause if isinstance(cause, httpx.HTTPStatusError) else None


def http_error_response(error: MCPError) -> httpx.Response | None:
    """Return the HTTP response behind an API error, if there was one."""
    cause = _http_status_error(error)
    return cause.response if cause is not None else None


def _is_auth_host_error(error: MCPError) -> bool:
    """Check whether the failed request went to the OAuth host.

    A 401 there concerns the app's client credentials, not the user's access
    token, so refreshing or clearing the stored token cannot help.
    """
    cause = _http_status_error(error)
    return cause is not None and is_auth_host_url(str(cause.request.url))


def _rejected_access_token(error: MCPError) -> str | None:
    """Return the access token the failed request actually sent.

    Read from the request rather than the client, which another coroutine may
    already have refreshed. None when the request carried no Bearer token, so
    the refresh only happens if the client's own token has expired.
    """
    cause = _http_status_error(error)
    header = cause.request.headers.get("Authorization") if cause else None
    if isinstance(header, str) and header.startswith("Bearer "):
        return header.removeprefix("Bearer ")
    return None


_token_refresh_in_progress: ContextVar[bool] = ContextVar(
    "trakt_token_refresh_in_progress", default=False
)


@contextmanager
def token_refresh_scope() -> Generator[None]:
    """Mark the current task as running a token refresh.

    A 401 raised inside the refresh must not start another refresh. This is
    task-local, unlike the process-wide refresh lock that other tasks share.
    """
    reset_token = _token_refresh_in_progress.set(True)
    try:
        yield
    finally:
        _token_refresh_in_progress.reset(reset_token)


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
        error_data = add_context_to_error_data(error_data, context)
    elif correlation_id is not None:
        error_data["correlation_id"] = correlation_id
    return error_data


async def _execute_with_error_handling[R](
    coro: Awaitable[R],
    *,
    on_401: Callable[[], None] | None = None,
    convert_errors_to_text: bool = False,
) -> R | str:
    """Execute an awaitable with shared error handling logic.

    Args:
        coro: The awaitable to execute
        on_401: Optional callback to invoke on 401 HTTP status (e.g., clear auth token)
        convert_errors_to_text: If True, convert MCPErrors to friendly text
            instead of re-raising. AuthenticationRequiredError gets special
            formatting via format_auth_required_message; all other MCPErrors
            become ``# Error\\n\\n{message}`` so FastMCP returns them as normal
            text instead of wrapping in ToolError.

    Returns:
        The awaited result of type R on success. When convert_errors_to_text is
        True and an MCPError is caught, returns a formatted str message instead
        of re-raising.

    Raises:
        MCPError: On API or internal errors (when convert_errors_to_text is False)
        ValueError, TypeError, KeyError, AttributeError: Re-raised as-is
    """
    from .error_handler import TraktAPIErrorHandler
    from .request_context import add_context_to_error_data, get_current_context

    context = get_current_context()
    correlation_id = context.correlation_id if context else None

    try:
        return await coro
    except httpx.HTTPStatusError as e:
        # Re-read context — the coroutine may have set it during execution
        context = get_current_context()
        correlation_id = context.correlation_id if context else correlation_id
        error = TraktAPIErrorHandler.handle_http_error(
            error=e,
            endpoint=context.endpoint if context else None,
            resource_type=context.resource_type if context else None,
            resource_id=context.resource_id if context else None,
            correlation_id=correlation_id,
        )
        if context:
            error.data = add_context_to_error_data(error.data or {}, context)

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
        if convert_errors_to_text:
            from .error_types import (
                AuthenticationRequiredError,
                extract_auth_action,
                format_auth_required_message,
            )

            if isinstance(e, AuthenticationRequiredError):
                return format_auth_required_message(extract_auth_action(e))
            # Convert all MCPErrors to formatted strings so FastMCP
            # returns them as normal text instead of wrapping in ToolError
            return f"# Error\n\n{e.message}"
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


def handle_api_errors[OwnerT, **P, R](
    method: Callable[Concatenate[OwnerT, P], Awaitable[R]],
) -> Callable[Concatenate[OwnerT, P], Awaitable[R | str]]:
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
    async def wrapper(self: OwnerT, /, *args: P.args, **kwargs: P.kwargs) -> R | str:
        try:
            # First attempt — do NOT clear token on 401 so refresh can recover
            return await _execute_with_error_handling(
                method(self, *args, **kwargs),
            )
        except MCPError as first_error:
            # Only a real HTTP 401 from the API host is recoverable here. A method
            # raising AuthenticationRequiredError after ensure_authenticated()
            # failed has already tried to refresh.
            if (
                not _is_auth_required_error(first_error)
                or _http_status_error(first_error) is None
                or _is_auth_host_error(first_error)
                or first_error.refresh_attempted
            ):
                raise
            first_error.refresh_attempted = True

            # A 401 inside refresh_access_token's own request: let it decide.
            if _token_refresh_in_progress.get():
                raise

            if isinstance(self, RefreshableAuthClient) and _has_refresh_token(self):
                try:
                    refreshed = await self.refresh_access_token(
                        rejected_access_token=_rejected_access_token(first_error)
                    )
                except Exception:
                    logger.warning(
                        "Token refresh failed during 401 recovery", exc_info=True
                    )
                    refreshed = False

                if refreshed:
                    try:
                        # Retry once with refreshed token
                        return await _execute_with_error_handling(
                            method(self, *args, **kwargs),
                        )
                    except MCPError as retry_error:
                        # The pair was just saved; a failed retry (404, 429, a
                        # network error, even another 401) does not make it dead.
                        retry_error.refresh_attempted = True
                        raise
                # Refresh failed. refresh_access_token already cleared a dead
                # (invalid_grant) token; anything else may be transient, and
                # deleting the refresh token would force a costly reconnect.
                raise

            # No refresh possible — the stored token is unusable.
            _auto_clear_invalid_token(self)
            raise

    return wrapper


def handle_api_errors_func[**P, R](
    func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R | str]]:
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
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | str:
        from .request_context import clear_current_context

        try:
            return await _execute_with_error_handling(
                func(*args, **kwargs),
                convert_errors_to_text=True,
            )
        finally:
            clear_current_context()

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
