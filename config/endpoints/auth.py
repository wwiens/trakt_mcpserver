"""Authentication endpoints."""

from typing import Final

AUTH_ENDPOINTS: Final[dict[str, str]] = {
    # Authentication endpoints
    "device_code": "/oauth/device/code",
    "device_token": "/oauth/device/token",
    "revoke": "/oauth/revoke",
}
