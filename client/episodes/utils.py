"""Shared utilities for episode client modules."""

from client.endpoints import build_endpoint
from client.validation import validate_media_id


def validate_show_id(show_id: str) -> str:
    """Strip and validate a show ID, returning the stripped value."""
    return validate_media_id(show_id, "show_id")


def validate_season(season: int) -> int:
    """Validate a season number.

    Args:
        season: Season number (0 for specials)

    Returns:
        Validated season number

    Raises:
        ValueError: If season is negative
    """
    if season < 0:
        msg = "season must be >= 0 (use 0 for specials)"
        raise ValueError(msg)
    return season


def validate_episode(episode: int) -> int:
    """Validate an episode number.

    Args:
        episode: Episode number (must be >= 1)

    Returns:
        Validated episode number

    Raises:
        ValueError: If episode is less than 1
    """
    if episode < 1:
        msg = "episode must be >= 1"
        raise ValueError(msg)
    return episode


def build_episode_endpoint(
    endpoint_key: str,
    show_id: str,
    season: int,
    episode: int,
    **replacements: str,
) -> str:
    """Build an episode API endpoint URL from a template.

    Args:
        endpoint_key: Key in TRAKT_ENDPOINTS (e.g., 'episode_summary')
        show_id: Already-validated show ID (will be URL-encoded)
        season: Season number
        episode: Episode number
        **replacements: Additional template replacements (e.g., language='en')

    Returns:
        Fully resolved endpoint URL
    """
    return build_endpoint(
        endpoint_key,
        id=show_id,
        season=season,
        episode=episode,
        **replacements,
    )
