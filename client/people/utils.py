"""Shared utilities for people client modules."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS


def validate_person_id(person_id: str) -> str:
    """Strip and validate a person ID, returning the stripped value.

    Args:
        person_id: Trakt ID, Trakt slug, or IMDB ID

    Returns:
        Stripped person_id

    Raises:
        ValueError: If person_id is empty after stripping
    """
    person_id = person_id.strip()
    if not person_id:
        msg = "person_id cannot be empty"
        raise ValueError(msg)
    return person_id


def build_person_endpoint(
    endpoint_key: str,
    person_id: str,
    **replacements: str,
) -> str:
    """Build a people API endpoint URL from a template.

    Args:
        endpoint_key: Key in TRAKT_ENDPOINTS (e.g., 'person_summary')
        person_id: Already-validated person ID (will be URL-encoded)
        **replacements: Additional template replacements (e.g., type='personal')

    Returns:
        Fully resolved endpoint URL
    """
    encoded_id = quote(person_id, safe="")
    endpoint = TRAKT_ENDPOINTS[endpoint_key].replace(":id", encoded_id)
    for placeholder, value in replacements.items():
        endpoint = endpoint.replace(f":{placeholder}", value)
    return endpoint
