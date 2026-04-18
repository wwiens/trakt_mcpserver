"""Check-in endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

CHECKIN_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    "checkin": "/checkin",
}
