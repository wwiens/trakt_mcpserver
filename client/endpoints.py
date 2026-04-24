"""Shared endpoint building utilities for client modules."""

from urllib.parse import quote

from config.endpoints import TRAKT_ENDPOINTS, EndpointKey


def build_endpoint(endpoint_key: EndpointKey, **replacements: str | int) -> str:
    """Build an API endpoint URL from a template with placeholder substitution.

    Looks up the endpoint template in TRAKT_ENDPOINTS, then replaces ``:placeholder``
    patterns with URL-encoded values.

    Args:
        endpoint_key: Key in TRAKT_ENDPOINTS (e.g., ``'episode_summary'``)
        **replacements: Mapping of placeholder names to values.
            Values are converted to strings and URL-encoded.
            Example: ``id="breaking-bad"``, ``season=1``, ``episode=3``

    Returns:
        Fully resolved endpoint URL
    """
    endpoint = TRAKT_ENDPOINTS[endpoint_key]
    for placeholder, value in replacements.items():
        encoded = quote(str(value), safe="")
        endpoint = endpoint.replace(f":{placeholder}", encoded)
    return endpoint
