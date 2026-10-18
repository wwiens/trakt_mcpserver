"""Authentication client for Trakt API."""

import asyncio
import logging
import os
import time
from http import HTTPStatus
from typing import Final

import httpx
from pydantic import ValidationError

from config.auth import (
    DEVICE_POLL_UNEXPECTED_MESSAGE,
    DEVICE_TOKEN_ERROR_MESSAGES,
    DEVICE_TOKEN_OAUTH_ERROR_STATUSES,
    DEVICE_TOKEN_PENDING_STATUS,
    DEVICE_TOKEN_REJECTED_MESSAGE,
    DEVICE_TOKEN_SLOW_DOWN_STATUS,
    INVALID_CLIENT_MESSAGE,
    OAUTH_ERROR_AUTHORIZATION_PENDING,
    OAUTH_ERROR_INVALID_CLIENT,
    OAUTH_ERROR_INVALID_GRANT,
    OAUTH_REDIRECT_URI,
)
from config.endpoints import TRAKT_ENDPOINTS
from models.auth import (
    DeviceTokenRequest,
    OAuthErrorResponse,
    TraktAuthToken,
    TraktDeviceCode,
)
from utils.api.error_types import (
    AuthorizationPendingError,
    DeviceAuthorizationError,
    TraktRateLimitError,
)
from utils.api.errors import (
    InvalidParamsError,
    InvalidRequestError,
    MCPError,
    handle_api_errors,
    http_error_response,
    token_refresh_scope,
)

from ..base import BaseClient
from .token_store import TokenStore, get_token_store

logger = logging.getLogger(__name__)

# User authentication token storage path.
# Default lives under the user's home so the token survives across uvx invocations
# (uvx's CWD is a throwaway temp dir). Override via TRAKT_AUTH_TOKEN_PATH —
# Docker images set it to /data/auth_token.json for volume-based persistence.
AUTH_TOKEN_FILE: Final[str] = os.environ.get(
    "TRAKT_AUTH_TOKEN_PATH",
    os.path.expanduser("~/.trakt-mcp/auth_token.json"),
)


def _oauth_error_body(response: httpx.Response) -> OAuthErrorResponse | None:
    """Parse an OAuth error body; None when it is empty or not a JSON object."""
    if not response.content:
        return None
    try:
        return OAuthErrorResponse.model_validate_json(response.content)
    except ValidationError:
        return None


def _is_invalid_client(
    response: httpx.Response, body: OAuthErrorResponse | None
) -> bool:
    """Trakt rejected the app's client credentials rather than the request."""
    return response.status_code == HTTPStatus.UNAUTHORIZED or (
        body is not None and body.error == OAUTH_ERROR_INVALID_CLIENT
    )


def _device_token_error(error: MCPError) -> MCPError | None:
    """Map a failed device-token poll to the error its HTTP status documents.

    Trakt answers these polls with empty bodies, so the generic HTTP error
    mapping cannot tell "still pending" or "denied" apart from real failures.
    Returns None when the status is outside the device-token contract.
    """
    response = http_error_response(error)
    # The generic handler already recognises an authorization_pending body.
    if response is None or isinstance(error, AuthorizationPendingError):
        return None
    body = _oauth_error_body(response)
    error_code = body.error if body else None
    status: int | None = response.status_code
    if _is_invalid_client(response, body):
        return DeviceAuthorizationError(
            http_status=response.status_code,
            message=INVALID_CLIENT_MESSAGE,
            restart_required=True,
        )
    if status == DEVICE_TOKEN_PENDING_STATUS:
        if not response.content or error_code == OAUTH_ERROR_AUTHORIZATION_PENDING:
            return AuthorizationPendingError()
        status = DEVICE_TOKEN_OAUTH_ERROR_STATUSES.get(error_code or "")
        if status is None:
            # A JSON OAuth error ends the flow; a non-OAuth body (e.g. a proxy
            # page) says nothing about the code, so keep polling after a pause.
            return DeviceAuthorizationError(
                http_status=response.status_code,
                message=(
                    DEVICE_TOKEN_REJECTED_MESSAGE
                    if body
                    else DEVICE_POLL_UNEXPECTED_MESSAGE
                ),
                restart_required=body is not None,
            )
    message = DEVICE_TOKEN_ERROR_MESSAGES.get(status)
    if message is None:
        return None
    rate_limited = isinstance(error, TraktRateLimitError)
    return DeviceAuthorizationError(
        http_status=status,
        message=message,
        restart_required=status != DEVICE_TOKEN_SLOW_DOWN_STATUS,
        retry_after=error.retry_after if rate_limited else None,
    )


class AuthClient(BaseClient):
    """Client for handling Trakt authentication.

    The token pair lives in the process-wide TokenStore for AUTH_TOKEN_FILE, so
    every AuthClient (one per tool call) sees the same, current pair.
    """

    def __init__(self):
        """Initialize the authentication client."""
        super().__init__()
        self._store: TokenStore = get_token_store(AUTH_TOKEN_FILE)
        self._store.sync_from_disk()
        self._update_headers_with_token()

    @property
    def auth_token(self) -> TraktAuthToken | None:
        """The current token pair, shared by every AuthClient in the process."""
        return self._store.token

    @auth_token.setter
    def auth_token(self, token: TraktAuthToken | None) -> None:
        self._store.token = token

    def _save_auth_token(self, token: TraktAuthToken) -> None:
        """Make ``token`` current, persist it and send it from now on."""
        self._store.save(token)
        self._update_headers_with_token()

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        if not self.auth_token:
            return False

        # Check if token is expired
        expiry = self.get_token_expiry()
        return expiry is not None and int(time.time()) < expiry

    def get_token_expiry(self) -> int | None:
        """Get the expiry timestamp of the current token."""
        if not self.auth_token:
            return None
        return self.auth_token.created_at + self.auth_token.expires_in

    def _with_client_secret(self, data: dict[str, str]) -> dict[str, str]:
        """Add the deprecated client_secret to an OAuth body when configured."""
        if self.client_secret:
            return {**data, "client_secret": self.client_secret}
        return data

    @handle_api_errors
    async def get_device_code(self) -> TraktDeviceCode:
        """Get a device code for authentication.

        Returns:
            Device code response from Trakt
        """
        data = {
            "client_id": self.client_id,
        }
        try:
            return await self._post_typed_request(
                TRAKT_ENDPOINTS["device_code"], data, response_type=TraktDeviceCode
            )
        except MCPError as error:
            response = http_error_response(error)
            if response is None or not _is_invalid_client(
                response, _oauth_error_body(response)
            ):
                raise
            raise InvalidRequestError(INVALID_CLIENT_MESSAGE) from error

    @handle_api_errors
    async def get_device_token(self, device_code: str) -> TraktAuthToken:
        """Exchange device code for an access token.

        Args:
            device_code: The device code to exchange

        Returns:
            Authentication token

        Raises:
            AuthorizationPendingError: The user has not approved the code yet.
            DeviceAuthorizationError: Trakt reported an invalid, used, expired
                or denied code, or asked to slow down.
            MCPError: Any other failure, as mapped by handle_api_errors.
        """
        # Validate input with Pydantic
        payload = DeviceTokenRequest.model_validate({"code": device_code})
        data = self._with_client_secret(
            {"code": payload.code, "client_id": self.client_id}
        )

        try:
            token = await self._post_typed_request(
                TRAKT_ENDPOINTS["device_token"], data, response_type=TraktAuthToken
            )
        except MCPError as error:
            mapped = _device_token_error(error)
            if mapped is None:
                raise
            raise mapped from error
        # The device code is now used up; the store keeps the pair in memory
        # even if saving fails, so the user does not have to log in again.
        self._save_auth_token(token)
        return token

    async def refresh_access_token(
        self, rejected_access_token: str | None = None
    ) -> bool:
        """Refresh the access token using the stored refresh token.

        Exchanges the refresh_token for a new access_token via the Trakt
        OAuth token endpoint. On success, saves the new token pair to disk.

        Refreshes are serialised across tool calls and server processes,
        since racing two refreshes with one single-use refresh token makes
        Trakt reject (and revoke) the loser.

        Args:
            rejected_access_token: Access token the API just rejected with 401.
                When given, refresh even if the token looks unexpired locally
                (server-side revocation, clock skew), unless another call has
                already replaced it.

        Returns:
            True if refresh succeeded, False if refresh failed
        """
        # Run the locked refresh as its own task. Cancelling the tool call must
        # not abandon a refresh Trakt may already have completed (the old
        # refresh token would be spent and the new pair lost), nor leave the
        # cross-process file lock held by a worker thread.
        return await asyncio.shield(self._locked_refresh(rejected_access_token))

    async def _locked_refresh(self, rejected_access_token: str | None) -> bool:
        """Take the refresh lock, then refresh."""
        async with self._store.refresh_lock():
            with token_refresh_scope():
                return await self._refresh_holding_lock(rejected_access_token)

    async def _refresh_holding_lock(self, rejected_access_token: str | None) -> bool:
        """Refresh the token; the caller holds the refresh lock."""
        # Another call or process may have refreshed or logged out meanwhile.
        self._store.sync_from_disk()
        self._update_headers_with_token()
        current = self.auth_token

        if rejected_access_token is None:
            if self.is_authenticated():
                return True
        elif current is not None and current.access_token != rejected_access_token:
            return True

        if not current or not current.refresh_token:
            return False

        data = self._with_client_secret(
            {
                "refresh_token": current.refresh_token,
                "client_id": self.client_id,
                "redirect_uri": OAUTH_REDIRECT_URI,
                "grant_type": "refresh_token",
            }
        )

        try:
            token = await self._post_typed_request(
                TRAKT_ENDPOINTS["token"], data, response_type=TraktAuthToken
            )
        except (InvalidRequestError, InvalidParamsError) as error:
            return self._handle_refresh_rejection(error, current.refresh_token)
        except (MCPError, ValueError):
            # Transient errors (network/timeout, 5xx) or an unparseable reply.
            # Keep the refresh token so the next attempt can succeed.
            logger.warning(
                "Failed to refresh access token (transient"
                + " error), keeping refresh token for next attempt",
                exc_info=True,
            )
            return False

        self._store.sync_from_disk()
        if self.auth_token is None:
            # Logged out while the refresh was in flight; honour that.
            self._update_headers_with_token()
            return False
        self._save_auth_token(token)
        logger.info("Successfully refreshed access token")
        return True

    def _handle_refresh_rejection(
        self, error: MCPError, sent_refresh_token: str
    ) -> bool:
        """Decide whether a rejected refresh means the stored token is dead.

        Returns:
            True if another process had already refreshed (its pair is adopted)
        """
        # Only invalid_grant means the token itself is dead; Trakt also sends
        # it for wrong client credentials, and revokes the token when it
        # does. Anything else (e.g. invalid_request for a malformed
        # TRAKT_REDIRECT_URI) leaves it usable, and clearing it would force a
        # reconnect, which costs a Community App connection.
        response = http_error_response(error)
        body = _oauth_error_body(response) if response is not None else None
        if body is None or body.error != OAUTH_ERROR_INVALID_GRANT:
            logger.warning(
                "Refresh request rejected (HTTP %s); keeping refresh token."
                + " Check TRAKT_CLIENT_ID and TRAKT_REDIRECT_URI.",
                response.status_code if response else "unknown",
            )
            return False
        # A server process without file locking (e.g. on Windows) may have won
        # the race and saved a fresh pair; that pair must not be deleted.
        self._store.sync_from_disk()
        self._update_headers_with_token()
        if (
            self.auth_token is not None
            and self.auth_token.refresh_token != sent_refresh_token
        ):
            return True
        logger.warning(
            "Refresh token rejected by server, clearing stale token",
            exc_info=True,
        )
        self.clear_auth_token()
        return False

    async def ensure_authenticated(self) -> bool:
        """Ensure the client is authenticated, refreshing the token if needed.

        Checks authentication status and attempts a token refresh when the
        access token has expired but a refresh token is available.

        Returns:
            True if authenticated (possibly after refresh), False otherwise
        """
        if self.is_authenticated():
            return True

        # Token exists but expired — try refreshing
        if self.auth_token and self.auth_token.refresh_token:
            return await self.refresh_access_token()

        return False

    def clear_auth_token(self) -> bool:
        """Clear the stored authentication token and delete the token file.

        Returns:
            True if token was cleared, False if no token existed or already cleared
        """
        # Always delete the file, even when it could not be loaded (corrupt).
        cleared = self._store.clear()
        self._update_headers_with_token()
        logger.debug("Cleared authentication token and Authorization header")
        return cleared
