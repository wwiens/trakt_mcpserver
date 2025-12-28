"""API constants for the Trakt MCP server."""

# API constants
DEFAULT_LIMIT = 10
DEFAULT_MAX_PAGES = 100  # Safety limit for auto-pagination
DEFAULT_FETCH_ALL_LIMIT = 100  # Safety cap when limit=0 (fetch all)


def effective_limit(limit: int) -> tuple[int, int]:
    """Calculate effective API limit and max_items for auto-pagination.

    When limit=0, users want to fetch all available results. This function
    converts that to appropriate values for the API (max per page) and
    for the result cap (safety limit).

    Args:
        limit: User-provided limit (0 = fetch all)

    Returns:
        Tuple of (api_limit, max_items) where:
        - api_limit: The limit to send to API (uses max per page when fetching all)
        - max_items: Maximum items to return (capped at DEFAULT_FETCH_ALL_LIMIT)
    """
    if limit > 0:
        return (limit, limit)
    return (100, DEFAULT_FETCH_ALL_LIMIT)
