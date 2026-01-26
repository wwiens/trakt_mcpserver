"""Datetime formatting utilities."""

from datetime import datetime
from typing import Final

DEFAULT_DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M"


def format_iso_timestamp(timestamp: str, fmt: str = DEFAULT_DATETIME_FORMAT) -> str:
    """Format an ISO 8601 timestamp to a human-readable string.

    Args:
        timestamp: ISO 8601 timestamp string (e.g., '2024-01-15T20:30:00.000Z')
        fmt: strftime format string

    Returns:
        Formatted datetime string, or original timestamp if parsing fails
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime(fmt)
    except ValueError:
        return timestamp
