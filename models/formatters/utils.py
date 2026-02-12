"""Shared formatting utilities for Trakt MCP server."""

from typing import Final, TypeVar

from models.types.pagination import PaginatedResponse
from utils.formatting import DISPLAY_DATETIME_FORMAT, format_iso_timestamp

T = TypeVar("T")

MAX_OVERVIEW_LENGTH: Final[int] = 200


def format_pagination_header(results: PaginatedResponse[T]) -> str:
    """Format pagination metadata and navigation hints.

    Args:
        results: Paginated response with metadata

    Returns:
        Formatted markdown string with page info and navigation
    """
    message = f"📄 **{results.page_info_summary()}**\n\n"

    # Add navigation hints if applicable
    if results.pagination.has_previous_page or results.pagination.has_next_page:
        nav_parts: list[str] = []
        if results.pagination.has_previous_page:
            nav_parts.append(f"Previous: page {results.pagination.previous_page()}")
        if results.pagination.has_next_page:
            nav_parts.append(f"Next: page {results.pagination.next_page()}")
        message += f"📍 **Navigation:** {' | '.join(nav_parts)}\n\n"

    return message


def format_display_time(timestamp: str) -> str:
    """Format ISO 8601 timestamp for display.

    Handles Trakt API timestamp format (ISO 8601 with 'Z' timezone).

    Args:
        timestamp: ISO 8601 timestamp string (e.g., "2023-01-01T12:34:56.789Z")

    Returns:
        Formatted timestamp string (e.g., "2023-01-01 12:34:56")
        Falls back to original string if parsing fails
    """
    return format_iso_timestamp(timestamp, fmt=DISPLAY_DATETIME_FORMAT)
