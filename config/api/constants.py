"""API constants for the Trakt MCP server."""

from typing import NamedTuple

# API constants
DEFAULT_LIMIT = 10
DEFAULT_MAX_PAGES = 100  # Safety limit for auto-pagination
DEFAULT_FETCH_ALL_LIMIT = 100  # Safety cap when limit=0 (fetch all)
MAX_API_PAGE_SIZE = 100  # Maximum items per page supported by Trakt API


class EffectiveLimit(NamedTuple):
    """Result of effective_limit() calculation for auto-pagination.

    Attributes:
        api_limit: The limit parameter to send to the API (items per page)
        max_items: Maximum total items to return (truncation cap)
    """

    api_limit: int
    max_items: int


def effective_limit(limit: int) -> EffectiveLimit:
    """Calculate effective API limit and max_items for auto-pagination.

    When limit=0, users want to fetch all available results. This function
    converts that to appropriate values for the API (max per page) and
    for the result cap (safety limit).

    Args:
        limit: User-provided limit (0 = fetch all, must be >= 0)

    Returns:
        EffectiveLimit with:
        - api_limit: The limit to send to API (uses max per page when fetching all)
        - max_items: Maximum items to return (capped at DEFAULT_FETCH_ALL_LIMIT)

    Raises:
        ValueError: If limit is negative
    """
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")
    if limit > 0:
        return EffectiveLimit(api_limit=limit, max_items=limit)
    return EffectiveLimit(
        api_limit=MAX_API_PAGE_SIZE, max_items=DEFAULT_FETCH_ALL_LIMIT
    )
