"""Utility functions for the Trakt MCP server."""

import functools
import logging
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

import httpx

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("trakt_mcp")

# Type for a generic async function
T = TypeVar("T")
AsyncFunc = Callable[..., Coroutine[Any, Any, T]]


def handle_api_errors(func: AsyncFunc[T]) -> AsyncFunc[T]:
    """Decorator to handle API errors gracefully.

    Args:
        func: The async function to wrap

    Returns:
        Wrapped function that handles API errors
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            status_code = e.response.status_code

            error_messages = {
                401: "Error: Unauthorized. Please check your Trakt API credentials.",
                404: "Error: The requested resource was not found.",
                429: "Error: Rate limit exceeded. Please try again later.",
            }
            return error_messages.get(
                status_code, f"Error: HTTP {status_code} - Please try again later."
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {e!s}")
            return "Error: Unable to connect to Trakt API. Please check your internet connection."
        except Exception as e:
            logger.exception("Unexpected error")
            return f"Error: An unexpected error occurred: {e!s}"

    return wrapper


def format_error_response(message: str) -> dict[str, Any]:
    """Format an error response for API errors.

    Args:
        message: The error message

    Returns:
        Formatted error response
    """
    return {
        "error": True,
        "message": message,
    }
