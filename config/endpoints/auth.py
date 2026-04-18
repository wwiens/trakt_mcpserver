"""Authentication endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

AUTH_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    "device_code": "/oauth/device/code",
    "device_token": "/oauth/device/token",
    "token": "/oauth/token",
    "revoke": "/oauth/revoke",
}
