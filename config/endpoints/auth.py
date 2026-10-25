"""Authentication endpoints."""

from collections.abc import Mapping
from typing import Final

from config.auth import TRAKT_AUTH_BASE_URL

from .keys import EndpointKey

AUTH_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    "device_code": f"{TRAKT_AUTH_BASE_URL}/oauth/device/code",
    "device_token": f"{TRAKT_AUTH_BASE_URL}/oauth/device/token",
    "token": f"{TRAKT_AUTH_BASE_URL}/oauth/token",
    "revoke": f"{TRAKT_AUTH_BASE_URL}/oauth/revoke",
}
