"""Helper functions for the Trakt MCP server."""

from typing import Any


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
