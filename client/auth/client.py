"""Authentication client for Trakt API."""

import json
import os
import time

from config.endpoints import TRAKT_ENDPOINTS
from models.auth import TraktAuthToken, TraktDeviceCode
from utils.api.errors import (  # pyright: ignore[reportUnusedImport] # Used by decorator
    handle_api_errors,
)

from ..base import BaseClient

# User authentication token storage path
AUTH_TOKEN_FILE = "auth_token.json"  # noqa: S105 # File path, not a password


class AuthClient(BaseClient):
    """Client for handling Trakt authentication."""

    def __init__(self):
        """Initialize the authentication client."""
        super().__init__()
        # Try to load auth token if exists
        self.auth_token = self._load_auth_token()
        if self.auth_token:
            self._update_headers_with_token()

    def _load_auth_token(self) -> TraktAuthToken | None:
        """Load authentication token from storage."""
        if os.path.exists(AUTH_TOKEN_FILE):
            try:
                with open(AUTH_TOKEN_FILE) as f:
                    token_data = json.load(f)
                    return TraktAuthToken(**token_data)
            except Exception as e:
                print(f"Error loading auth token: {e}")
        return None

    def _save_auth_token(self, token: TraktAuthToken):
        """Save authentication token to storage."""
        with open(AUTH_TOKEN_FILE, "w") as f:
            f.write(json.dumps(token.model_dump()))

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
        response = await self._post_request(TRAKT_ENDPOINTS["device_code"], data)
        # Validate with Pydantic model and return directly
        return TraktDeviceCode.model_validate(response)

    @handle_api_errors
    async def get_device_token(self, device_code: str) -> TraktAuthToken:
        """Exchange device code for an access token.

        Args:
            device_code: The device code to exchange

        Returns:
            Authentication token

        Raises:
            AuthorizationPendingError: If user hasn't authorized yet
            InternalError: If there's a server error
        """
        data = {
            "code": device_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = await self._post_request(TRAKT_ENDPOINTS["device_token"], data)
        token = TraktAuthToken(**response)
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
            except Exception as e:
                print(f"Error clearing auth token: {e}")
                return False
        return False
