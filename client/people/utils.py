"""Shared utilities for people client modules."""

import re
from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS

_IMDB_PATTERN: re.Pattern[str] = re.compile(r"^tt\d+$")


def validate_person_id(person_id: str) -> str:
    """Strip and validate a person ID, returning the stripped value.

    Accepts all five Trakt identifier types:
    - Trakt numeric ID (e.g. ``"12345"``)
    - Trakt slug (e.g. ``"bryan-cranston"``)
    - IMDB ID (format ``tt\\d+``, e.g. ``"tt0186151"``)
    - TMDB numeric ID
    - TVDB numeric ID

    Args:
        person_id: Trakt ID, slug, IMDB ID, TMDB ID, or TVDB ID

    Returns:
        Stripped person_id

    Raises:
        ValueError: If person_id is empty or has an invalid IMDB format
    """
    person_id = person_id.strip()
    if not person_id:
        msg = "person_id cannot be empty"
        raise ValueError(msg)

    if person_id.startswith("tt") and not _IMDB_PATTERN.match(person_id):
        msg = f"Invalid IMDB ID format: '{person_id}'. Expected format: tt followed by digits (e.g. tt0186151)"
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
