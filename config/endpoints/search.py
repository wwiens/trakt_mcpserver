"""Search endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

SEARCH_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    # Search endpoints
    "search": "/search",
}
