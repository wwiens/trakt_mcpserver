"""Shared utilities for people client modules."""

from client.endpoints import build_endpoint
from client.validation import validate_media_id
from config.endpoints import EndpointKey


def validate_person_id(person_id: str) -> str:
    """Strip and validate a person ID, returning the stripped value."""
    return validate_media_id(person_id, "person_id")


def build_person_endpoint(
    endpoint_key: EndpointKey,
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
    return build_endpoint(
        endpoint_key,
        id=person_id,
        **replacements,
    )
