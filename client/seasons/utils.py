"""Shared utilities for season client modules."""

from client.endpoints import build_endpoint
from client.validation import validate_media_id
from config.endpoints import EndpointKey


def validate_show_id(show_id: str) -> str:
    """Strip and validate a show ID, returning the stripped value."""
    return validate_media_id(show_id, "show_id")


def build_season_endpoint(
    endpoint_key: EndpointKey,
    show_id: str,
    season: int,
    **replacements: str,
) -> str:
    """Build a season API endpoint URL from a template.

    Args:
        endpoint_key: Key in TRAKT_ENDPOINTS (e.g., 'season_info')
        show_id: Already-validated show ID (will be URL-encoded)
        season: Season number
        **replacements: Additional template replacements (e.g., language='en')

    Returns:
        Fully resolved endpoint URL
    """
    return build_endpoint(
        endpoint_key,
        id=show_id,
        season=season,
        **replacements,
    )
