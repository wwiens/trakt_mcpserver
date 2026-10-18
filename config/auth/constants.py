"""Authentication constants for the Trakt MCP server."""

import os
from collections.abc import Mapping
from typing import Final
from urllib.parse import urlsplit

# Authentication constants
AUTH_POLL_INTERVAL: Final[int] = 5  # seconds
AUTH_EXPIRATION: Final[int] = 600  # seconds (10 minutes)
# Trakt requires all OAuth requests to use this host, not the API host.
TRAKT_AUTH_HOST: Final[str] = "auth.trakt.tv"
TRAKT_AUTH_BASE_URL: Final[str] = f"https://{TRAKT_AUTH_HOST}"
AUTH_VERIFICATION_URL: Final[str] = f"{TRAKT_AUTH_BASE_URL}/activate"


def is_auth_host_url(url: str) -> bool:
    """Check whether a URL targets the OAuth host rather than the API host."""
    return urlsplit(url).hostname == TRAKT_AUTH_HOST


# Required by the refresh-token exchange even though device flow has no callback.
# Trakt validates only the format (HTTPS, loopback HTTP, or OOB), not the app's
# registered list, so the default also works for older OOB-registered apps.
# `or` also covers a variable that is set but blank (e.g. `-e TRAKT_REDIRECT_URI=`).
OAUTH_REDIRECT_URI: Final[str] = (
    os.environ.get("TRAKT_REDIRECT_URI") or "http://localhost"
)

INVALID_CLIENT_MESSAGE: Final[str] = (
    "Trakt rejected the app's Client ID (invalid_client). Check that "
    "TRAKT_CLIENT_ID matches the Client ID shown on developer.trakt.tv."
)

_RESTART: Final[str] = "Start a new login with the `start_device_auth` tool."
DEVICE_TOKEN_REJECTED_MESSAGE: Final[str] = (
    f"Trakt rejected the device code request. {_RESTART}"
)
# Shown when a token looks valid locally but tools still report auth errors,
# e.g. after Trakt rejected it for a reason that did not clear it.
STALE_LOGIN_HINT: Final[str] = (
    "If tools still report that authentication is required, run `clear_auth` "
    "and then `start_device_auth` to log in again."
)
# Statuses documented for POST /oauth/device/token; Trakt sends them with no body.
DEVICE_TOKEN_PENDING_STATUS: Final[int] = 400
DEVICE_TOKEN_SLOW_DOWN_STATUS: Final[int] = 429
# RFC 8628 section 3.5: on slow_down, increase the polling interval by 5 seconds.
DEVICE_TOKEN_SLOW_DOWN_INCREMENT: Final[int] = 5
# RFC 8628 section 3.5 error codes, mapped to Trakt's equivalent statuses, in
# case auth.trakt.tv answers with a JSON 400 instead of a bare status.
DEVICE_TOKEN_OAUTH_ERROR_STATUSES: Final[Mapping[str, int]] = {
    "slow_down": DEVICE_TOKEN_SLOW_DOWN_STATUS,
    "expired_token": 410,
    "access_denied": 418,
}
DEVICE_TOKEN_ERROR_MESSAGES: Final[Mapping[int, str]] = {
    404: f"Trakt did not recognise this device code. {_RESTART}",
    409: f"This device code has already been used. {_RESTART}",
    410: f"The device code expired before it was approved. {_RESTART}",
    418: (
        "Trakt denied this device code. Either Deny was clicked, or the "
        "signed-in account cannot use this app: Development apps only allow "
        "the app owner and users added on developer.trakt.tv. "
        f"{_RESTART}"
    ),
    DEVICE_TOKEN_SLOW_DOWN_STATUS: "Trakt asked to slow down status checks.",
}
