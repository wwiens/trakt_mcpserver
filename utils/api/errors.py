"""Decorators and error handling for the Trakt MCP server."""

import functools
import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

import httpx

from config.errors import (
    ACCESS_FORBIDDEN,
    API_UNAVAILABLE,
    AUTH_REQUIRED,
    BAD_REQUEST,
    NETWORK_ERROR,
    RATE_LIMITED,
    RESOURCE_NOT_FOUND,
    UNPROCESSABLE_ENTITY,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("trakt_mcp")

# Standard MCP error codes (JSON-RPC 2.0)
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# Type for a generic async function
T = TypeVar("T")
AsyncFunc = Callable[..., Coroutine[Any, Any, T]]


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


def handle_api_errors(func: AsyncFunc[T]) -> AsyncFunc[T]:
    """Decorator to handle API errors gracefully with MCP-compliant error responses.

    Args:
        func: The async function to wrap

    Returns:
        Wrapped function that handles API errors using MCP error format
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            status_code = e.response.status_code

            # Map HTTP status codes to MCP error types
            if status_code == 400:
                raise InvalidRequestError(
                    BAD_REQUEST,
                    data={"http_status": status_code},
                ) from e
            elif status_code == 401:
                raise InvalidRequestError(
                    AUTH_REQUIRED,
                    data={"http_status": status_code},
                ) from e
            elif status_code == 403:
                raise InvalidRequestError(
                    ACCESS_FORBIDDEN,
                    data={"http_status": status_code},
                ) from e
            elif status_code == 404:
                raise InvalidRequestError(
                    RESOURCE_NOT_FOUND.format(
                        resource_type="resource", identifier="requested"
                    ),
                    data={"http_status": status_code},
                ) from e
            elif status_code == 422:
                raise InvalidRequestError(
                    UNPROCESSABLE_ENTITY,
                    data={"http_status": status_code},
                ) from e
            elif status_code == 429:
                raise InvalidRequestError(
                    RATE_LIMITED,
                    data={"http_status": status_code},
                ) from e
            else:
                raise InternalError(
                    f"HTTP {status_code} error occurred",
                    data={"http_status": status_code, "response": e.response.text},
                ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error: {e!s}")
            raise InternalError(
                NETWORK_ERROR,
                data={"error_type": "request_error", "details": str(e)},
            ) from e
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e!s}")
            raise InternalError(
                API_UNAVAILABLE,
                data={"error_type": "json_decode_error", "details": str(e)},
            ) from e
        except MCPError:
            # Re-raise MCP errors as-is
            raise
        except (ValueError, TypeError, KeyError, AttributeError):
            # Re-raise business logic errors as-is
            raise
        except Exception as e:
            logger.exception("Unexpected error")
            raise InternalError(
                f"An unexpected error occurred: {e!s}",
                data={"error_type": "unexpected_error"},
            ) from e

    return wrapper
