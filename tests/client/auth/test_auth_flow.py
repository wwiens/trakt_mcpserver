import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.auth import AuthClient
from models.auth import TraktAuthToken, TraktDeviceCode
from utils.api.error_types import AuthorizationPendingError, DeviceAuthorizationError
from utils.api.errors import InvalidRequestError, MCPError


@pytest.mark.asyncio
async def test_complete_device_auth_flow():
    device_code_response = {
        "device_code": "device_code_123",
        "user_code": "USER123",
        "verification_url": "https://auth.trakt.tv/activate",
        "expires_in": 600,
        "interval": 5,
    }

    auth_token_response = {
        "access_token": "access_token_123",
        "refresh_token": "refresh_token_123",
        "expires_in": 7200,
        "created_at": int(time.time()),
        "scope": "public",
        "token_type": "bearer",
    }

    mock_responses = [
        MagicMock(
            json=MagicMock(return_value=device_code_response),
            raise_for_status=MagicMock(),
        ),
        MagicMock(
            json=MagicMock(return_value=auth_token_response),
            raise_for_status=MagicMock(),
        ),
    ]

    from client.auth.client import AUTH_TOKEN_FILE

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(side_effect=mock_responses)
        mock_instance.get = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = AuthClient()

        device_code = await client.get_device_code()
        assert not isinstance(device_code, str)
        assert isinstance(device_code, TraktDeviceCode)
        assert device_code.device_code == "device_code_123"
        assert device_code.user_code == "USER123"

        auth_token = await client.get_device_token(device_code.device_code)
        assert not isinstance(auth_token, str)
        assert isinstance(auth_token, TraktAuthToken)
        assert auth_token.access_token == "access_token_123"
        assert auth_token.refresh_token == "refresh_token_123"

        assert client.is_authenticated() is True

    try:
        with open(AUTH_TOKEN_FILE, encoding="utf-8") as token_file:
            saved = TraktAuthToken.model_validate_json(token_file.read())
        assert saved.access_token == "access_token_123"
    finally:
        os.remove(AUTH_TOKEN_FILE)


# Test removed as refresh_token method doesn't exist in AuthClient


@pytest.mark.asyncio
async def test_auth_expiration_handling():
    current_time = int(time.time())

    valid_token = TraktAuthToken(
        access_token="valid_token",
        refresh_token="refresh_token_1",
        expires_in=7200,
        created_at=current_time - 1000,  # Created 1000 seconds ago, expires in 7200
        scope="public",
        token_type="bearer",
    )

    expired_token = TraktAuthToken(
        access_token="expired_token",
        refresh_token="refresh_token_3",
        expires_in=7200,
        created_at=current_time - 8000,  # Created 8000 seconds ago, expires in 7200
        scope="public",
        token_type="bearer",
    )

    with patch.dict(
        os.environ, {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"}
    ):
        # Test with valid token
        client = AuthClient()
        client.auth_token = valid_token
        assert client.is_authenticated() is True

        # Test with expired token
        client.auth_token = expired_token
        assert client.is_authenticated() is False


@pytest.mark.asyncio
async def test_device_token_pending_authorization():
    """Test getting a device token when the user hasn't authorized yet."""
    # Mock a 400 error response for pending authorization
    mock_error_response = MagicMock()
    mock_error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=MagicMock(),
        response=MagicMock(status_code=400, text="authorization_pending"),
    )

    # Patch the AsyncClient to return our mock error response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("os.path.exists", return_value=False),  # No existing auth token
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_error_response)
        mock_instance.get = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = AuthClient()

        # Try to get a token, should raise AuthorizationPendingError (auth pending)
        with pytest.raises(AuthorizationPendingError) as exc_info:
            await client.get_device_token("device_code_123")

        # Verify the error is of the correct type
        assert (
            exc_info.value.data
            and exc_info.value.data.get("error_type") == "auth_pending"
        )

        # Verify the client is not authenticated
        assert client.is_authenticated() is False


@pytest.mark.asyncio
async def test_device_token_expired():
    """Test getting a device token when the code has expired."""
    # Mock a 400 error response for expired code
    mock_error_response = MagicMock()
    mock_error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=MagicMock(),
        response=MagicMock(status_code=400, text="expired_token"),
    )

    # Patch the AsyncClient to return our mock error response
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("os.path.exists", return_value=False),  # No existing auth token
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_error_response)
        mock_instance.get = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = AuthClient()

        # A non-OAuth 400 body says nothing about the code: back off, keep it
        with pytest.raises(DeviceAuthorizationError) as exc_info:
            await client.get_device_token("device_code_123")

        assert exc_info.value.restart_required is False
        assert "may still be valid" in exc_info.value.message

        # Verify the client is not authenticated
        assert client.is_authenticated() is False


async def _poll_device_token_with_status(
    status: int, body: bytes = b"", headers: dict[str, str] | None = None
) -> None:
    """Poll the device token endpoint against a mocked HTTP status."""
    response = httpx.Response(
        status,
        content=body,
        headers=headers,
        request=httpx.Request("POST", "https://auth.trakt.tv/oauth/device/token"),
    )
    mock_error_response = MagicMock()
    mock_error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error", request=MagicMock(), response=response
    )
    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("os.path.exists", return_value=False),
        patch.dict(os.environ, {"TRAKT_CLIENT_ID": "test_id"}),
    ):
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_error_response)
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance
        await AuthClient().get_device_token("device_code_123")


@pytest.mark.asyncio
async def test_device_token_empty_400_is_pending():
    """Trakt signals 'pending' with a bodyless 400."""
    with pytest.raises(AuthorizationPendingError):
        await _poll_device_token_with_status(400)


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [404, 409, 410, 418])
async def test_device_token_terminal_statuses_require_restart(status: int):
    """Invalid, used, expired and denied codes need a new device code."""
    with pytest.raises(DeviceAuthorizationError) as exc_info:
        await _poll_device_token_with_status(status)

    assert exc_info.value.restart_required is True
    assert exc_info.value.data == {"error_type": "device_auth", "http_status": status}
    assert "start_device_auth" in exc_info.value.message


@pytest.mark.asyncio
async def test_device_token_denied_explains_development_app_restriction():
    """418 mentions the Development-app user restriction seen in practice."""
    with pytest.raises(DeviceAuthorizationError) as exc_info:
        await _poll_device_token_with_status(418)

    assert "Development apps" in exc_info.value.message


@pytest.mark.asyncio
async def test_device_token_slow_down_keeps_flow():
    """429 slow-down is recoverable; polling may continue with the same code."""
    with pytest.raises(DeviceAuthorizationError) as exc_info:
        await _poll_device_token_with_status(429)

    assert exc_info.value.restart_required is False


@pytest.mark.asyncio
async def test_device_token_unmapped_status_keeps_generic_error():
    """Statuses outside the device-token contract keep the generic mapping."""
    with pytest.raises(MCPError) as exc_info:
        await _poll_device_token_with_status(500)

    assert not isinstance(exc_info.value, DeviceAuthorizationError)
    assert isinstance(exc_info.value.__cause__, httpx.HTTPStatusError)


@pytest.mark.asyncio
async def test_device_token_json_authorization_pending_is_pending():
    """An explicit RFC 8628 authorization_pending body is also 'pending'."""
    with pytest.raises(AuthorizationPendingError):
        await _poll_device_token_with_status(400, b'{"error": "authorization_pending"}')


@pytest.mark.asyncio
async def test_device_token_json_400_without_error_code_is_not_pending():
    """Only an empty body or an explicit code means pending, not any JSON."""
    with pytest.raises(MCPError) as exc_info:
        await _poll_device_token_with_status(400, b"{}")

    assert not isinstance(exc_info.value, AuthorizationPendingError)


@pytest.mark.asyncio
async def test_device_token_400_with_other_oauth_error_is_not_pending():
    with pytest.raises(MCPError) as exc_info:
        await _poll_device_token_with_status(400, b'{"error": "invalid_client"}')

    assert not isinstance(exc_info.value, AuthorizationPendingError)


@pytest.mark.asyncio
async def test_device_token_slow_down_carries_retry_after():
    with pytest.raises(DeviceAuthorizationError) as exc_info:
        await _poll_device_token_with_status(429, headers={"Retry-After": "12"})

    assert exc_info.value.retry_after == 12


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("oauth_error", "expected_status", "restart_required"),
    [
        ("slow_down", 429, False),
        ("expired_token", 410, True),
        ("access_denied", 418, True),
    ],
)
async def test_device_token_rfc8628_json_errors(
    oauth_error: str, expected_status: int, restart_required: bool
):
    """RFC 8628 JSON 400 errors map to the same handling as Trakt's statuses."""
    body = f'{{"error": "{oauth_error}"}}'.encode()
    with pytest.raises(DeviceAuthorizationError) as exc_info:
        await _poll_device_token_with_status(400, body)

    assert exc_info.value.data == {
        "error_type": "device_auth",
        "http_status": expected_status,
    }
    assert exc_info.value.restart_required is restart_required


@pytest.mark.asyncio
async def test_device_code_invalid_client_keeps_stored_token():
    """A mistyped TRAKT_CLIENT_ID (401 invalid_client) must not delete the token.

    The 401 concerns the app, not the user's token: no refresh is attempted
    (Trakt would revoke the token) and auth_token.json is left alone.
    """
    request = httpx.Request("POST", "https://auth.trakt.tv/oauth/device/code")
    response = httpx.Response(
        401,
        json={"error": "invalid_client", "error_description": "client not found"},
        request=request,
    )
    mock_error_response = MagicMock()
    mock_error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized", request=request, response=response
    )
    expired_token = TraktAuthToken(
        access_token="expired_access",
        refresh_token="still_valid_refresh",
        expires_in=3600,
        created_at=int(time.time()) - 7200,
    )

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("os.path.exists", return_value=False),
        patch("os.remove") as mock_remove,
        patch.dict(os.environ, {"TRAKT_CLIENT_ID": "mistyped_id"}),
    ):
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_error_response)
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = AuthClient()
        client.auth_token = expired_token

        with pytest.raises(InvalidRequestError) as exc_info:
            await client.get_device_code()

    assert "TRAKT_CLIENT_ID" in exc_info.value.message
    assert client.auth_token is expired_token
    mock_remove.assert_not_called()
    # Only the device-code call; no refresh attempt against /oauth/token.
    assert mock_instance.post.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "body"),
    [(401, b'{"error": "invalid_client"}'), (400, b'{"error": "invalid_client"}')],
)
async def test_device_token_invalid_client_explains_credentials(
    status: int, body: bytes
):
    """Bad client credentials while polling end the flow with a clear message."""
    with pytest.raises(DeviceAuthorizationError) as exc_info:
        await _poll_device_token_with_status(status, body)

    assert exc_info.value.restart_required is True
    assert "TRAKT_CLIENT_ID" in exc_info.value.message
