"""Datetime formatting utilities."""

from datetime import datetime
from typing import Final

DEFAULT_DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M"
DISPLAY_DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def format_iso_timestamp(
    timestamp: str | datetime, fmt: str = DEFAULT_DATETIME_FORMAT
) -> str:
    """Format an ISO 8601 timestamp to a human-readable string.

    Args:
        timestamp: ISO 8601 timestamp string or datetime object
        fmt: strftime format string

    Returns:
        Formatted datetime string, or original timestamp if parsing fails
    """
    if isinstance(timestamp, datetime):
        return timestamp.strftime(fmt)
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime(fmt)
    except ValueError:
        return timestamp
