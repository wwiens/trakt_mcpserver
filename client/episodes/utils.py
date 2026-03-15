"""Shared utilities for episode client modules."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS


def validate_show_id(show_id: str) -> str:
    """Strip and validate a show ID, returning the stripped value.

    Args:
        show_id: Trakt ID, slug, or IMDB ID

    Returns:
        Stripped show_id

    Raises:
        ValueError: If show_id is empty after stripping
    """
    show_id = show_id.strip()
    if not show_id:
        msg = "show_id cannot be empty"
        raise ValueError(msg)
    return show_id


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
    encoded_id = quote(show_id, safe="")
    endpoint = (
        TRAKT_ENDPOINTS[endpoint_key]
        .replace(":id", encoded_id)
        .replace(":season", str(season))
        .replace(":episode", str(episode))
    )
    for placeholder, value in replacements.items():
        endpoint = endpoint.replace(f":{placeholder}", value)
    return endpoint
