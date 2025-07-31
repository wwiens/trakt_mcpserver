"""Input validation utilities for the Trakt MCP server."""

import re

from config.errors import (
    EMPTY_QUERY,
    INVALID_ID,
    INVALID_PARAMETER,
    VALID_TRAKT_ID_PATTERN,
)
from utils.api.errors import InvalidParamsError


def validate_non_empty_string(value: str, param_name: str) -> None:
    """Validate that a string parameter is not empty or whitespace-only.

    Args:
        value: The string value to validate
        param_name: Name of the parameter for error messages

    Raises:
        InvalidParamsError: If the string is empty or whitespace-only
    """
    if not value or not value.strip():
        if param_name == "query":
            raise InvalidParamsError(EMPTY_QUERY)
        raise InvalidParamsError(
            INVALID_PARAMETER.format(parameter=param_name, reason="cannot be empty")
        )


def validate_trakt_id(value: str, resource_type: str) -> None:
    """Validate that a string is a valid Trakt ID (numeric).

    Args:
        value: The ID string to validate
        resource_type: Type of resource (e.g., "show", "movie", "comment")

    Raises:
        InvalidParamsError: If the ID format is invalid
    """
    if not re.match(VALID_TRAKT_ID_PATTERN, value):
        raise InvalidParamsError(
            INVALID_ID.format(resource_type=resource_type, id=value)
        )


def validate_positive_integer(
    value: int, param_name: str, allow_zero: bool = False
) -> None:
    """Validate that an integer parameter is positive (or zero if allowed).

    Args:
        value: The integer value to validate
        param_name: Name of the parameter for error messages
        allow_zero: Whether to allow zero as a valid value

    Raises:
        InvalidParamsError: If the integer is negative or zero (when not allowed)
    """
    min_value = 0 if allow_zero else 1
    if value < min_value:
        min_desc = "non-negative" if allow_zero else "positive"
        raise InvalidParamsError(
            INVALID_PARAMETER.format(
                parameter=param_name, reason=f"must be {min_desc} (got {value})"
            )
        )


def validate_limit(value: int) -> None:
    """Validate a limit parameter.

    Args:
        value: The limit value to validate

    Raises:
        InvalidParamsError: If the limit is negative or unreasonably large
    """
    if value < 0:
        raise InvalidParamsError(
            INVALID_PARAMETER.format(parameter="limit", reason="cannot be negative")
        )
    if value > 1000:
        raise InvalidParamsError(
            INVALID_PARAMETER.format(parameter="limit", reason="cannot exceed 1000")
        )


def validate_year(value: int | None) -> None:
    """Validate a year parameter.

    Args:
        value: The year value to validate (can be None)

    Raises:
        InvalidParamsError: If the year is unreasonable
    """
    if value is not None:
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1800 or value > current_year + 10:
            raise InvalidParamsError(
                INVALID_PARAMETER.format(
                    parameter="year",
                    reason=f"must be between 1800 and {current_year + 10} (got {value})",
                )
            )


def validate_episode_season(season: int, episode: int) -> None:
    """Validate season and episode numbers.

    Args:
        season: The season number to validate
        episode: The episode number to validate

    Raises:
        InvalidParamsError: If season or episode numbers are invalid
    """
    if season < 1:
        raise InvalidParamsError(
            INVALID_PARAMETER.format(
                parameter="season", reason=f"must be at least 1 (got {season})"
            )
        )
    if episode < 1:
        raise InvalidParamsError(
            INVALID_PARAMETER.format(
                parameter="episode", reason=f"must be at least 1 (got {episode})"
            )
        )
    if season > 100:  # Reasonable upper limit
        raise InvalidParamsError(
            INVALID_PARAMETER.format(
                parameter="season", reason=f"unreasonably high (got {season})"
            )
        )
    if episode > 1000:  # Reasonable upper limit
        raise InvalidParamsError(
            INVALID_PARAMETER.format(
                parameter="episode", reason=f"unreasonably high (got {episode})"
            )
        )


def validate_sort_option(value: str, valid_options: list[str]) -> None:
    """Validate a sort parameter against allowed values.

    Args:
        value: The sort value to validate
        valid_options: List of valid sort options

    Raises:
        InvalidParamsError: If the sort option is not valid
    """
    if value not in valid_options:
        raise InvalidParamsError(
            INVALID_PARAMETER.format(
                parameter="sort",
                reason=f"must be one of {', '.join(valid_options)} (got '{value}')",
            )
        )


def validate_period_option(value: str) -> None:
    """Validate a period parameter for trending content.

    Args:
        value: The period value to validate

    Raises:
        InvalidParamsError: If the period is not valid
    """
    valid_periods = ["daily", "weekly", "monthly", "yearly", "all"]
    if value not in valid_periods:
        raise InvalidParamsError(
            INVALID_PARAMETER.format(
                parameter="period",
                reason=f"must be one of {', '.join(valid_periods)} (got '{value}')",
            )
        )
