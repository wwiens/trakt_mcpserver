"""Authentication client for Trakt API."""

import contextlib
import json
import logging
import os
import time

from config.endpoints import TRAKT_ENDPOINTS
from models.auth import DeviceTokenRequest, TraktAuthToken, TraktDeviceCode
from utils.api.errors import handle_api_errors

from ..base import BaseClient

logger = logging.getLogger(__name__)

# User authentication token storage path
AUTH_TOKEN_FILE = "auth_token.json"  # noqa: S105 # File path, not a password


class AuthClient(BaseClient):
    """Client for handling Trakt authentication."""

    def __init__(self):
        """Initialize the authentication client."""
        super().__init__()
        # Try to load auth token if exists
        self.auth_token: TraktAuthToken | None = self._load_auth_token()
        if self.auth_token:
            self._update_headers_with_token()

    def _load_auth_token(self) -> TraktAuthToken | None:
        """Load authentication token from storage."""
        if os.path.exists(AUTH_TOKEN_FILE):
            try:
                with open(AUTH_TOKEN_FILE) as f:
                    token_data = json.load(f)
                    return TraktAuthToken.model_validate(token_data)
            except Exception:
                logger.exception("Error loading auth token")
        return None

    def _save_auth_token(self, token: TraktAuthToken) -> None:
        """Save authentication token to storage."""
        # Create file with secure permissions (user read/write only)
        fd = os.open(AUTH_TOKEN_FILE, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        try:
            file_obj = os.fdopen(fd, "w", encoding="utf-8")
            with file_obj:
                file_obj.write(token.model_dump_json())
                file_obj.flush()
                # fsync may not be available on all file objects or platforms
                with contextlib.suppress(OSError, AttributeError, TypeError):
                    os.fsync(file_obj.fileno())
        except Exception:
            # If fdopen failed, ensure we close the raw FD without masking the original error.
            with contextlib.suppress(OSError):
                os.close(fd)
            raise

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        if not self.auth_token:
            return False

        # Check if token is expired
        current_time = int(time.time())
        token_expiry = self.auth_token.created_at + self.auth_token.expires_in
        return current_time < token_expiry

    def get_token_expiry(self) -> int | None:
        """Get the expiry timestamp of the current token."""
        if not self.auth_token:
            return None
        return self.auth_token.created_at + self.auth_token.expires_in

    @handle_api_errors
    async def get_device_code(self) -> TraktDeviceCode:
        """Get a device code for authentication.

        Returns:
            Device code response from Trakt
        """
        data = {
            "client_id": self.client_id,
        }
        return await self._post_typed_request(
            TRAKT_ENDPOINTS["device_code"], data, response_type=TraktDeviceCode
        )

    @handle_api_errors
    async def get_device_token(self, device_code: str) -> TraktAuthToken:
        """Exchange device code for an access token.

        Args:
            device_code: The device code to exchange

        Returns:
            Authentication token

        Raises:
            AuthenticationError: Authorization pending or denied.
            NetworkError: Connectivity or timeout issues.
            InternalError: Unexpected server or parsing failures.
        """
        # Validate input with Pydantic
        payload = DeviceTokenRequest.model_validate({"code": device_code})
        data = {
            "code": payload.code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        token = await self._post_typed_request(
            TRAKT_ENDPOINTS["device_token"], data, response_type=TraktAuthToken
        )
        self.auth_token = token
        self._save_auth_token(token)
        self._update_headers_with_token()
        return token

    def clear_auth_token(self) -> bool:
        """Clear the stored authentication token.

        Returns:
            True if token was cleared, False if no token existed
        """
        if os.path.exists(AUTH_TOKEN_FILE):
            try:
                os.remove(AUTH_TOKEN_FILE)
                self.auth_token = None
                # Remove auth header
                if "Authorization" in self.headers:
                    del self.headers["Authorization"]
                return True
            except Exception:
                logger.exception("Error clearing auth token")
                return False
        return False
