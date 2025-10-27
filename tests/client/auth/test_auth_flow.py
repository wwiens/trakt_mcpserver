import os
import time
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest

from client.auth import AuthClient
from models.auth import TraktAuthToken, TraktDeviceCode
from utils.api.error_types import AuthorizationPendingError
from utils.api.errors import InvalidParamsError


@pytest.mark.asyncio
async def test_complete_device_auth_flow():
    device_code_response = {
        "device_code": "device_code_123",
        "user_code": "USER123",
        "verification_url": "https://trakt.tv/activate",
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

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("builtins.open", mock_open()) as mock_file,
        patch("json.dumps", return_value="{}"),
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
        assert isinstance(device_code, TraktDeviceCode)
        assert device_code.device_code == "device_code_123"
        assert device_code.user_code == "USER123"

        auth_token = await client.get_device_token(device_code.device_code)
        assert isinstance(auth_token, TraktAuthToken)
        assert auth_token.access_token == "access_token_123"
        assert auth_token.refresh_token == "refresh_token_123"

        assert client.is_authenticated() is True

        assert mock_file.called


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
        patch("client.base.load_dotenv"),  # Mock dotenv loading
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

        # Try to get a token, should raise AuthorizationPendingError because authorization is pending
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
        patch("client.base.load_dotenv"),  # Mock dotenv loading
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

        # Try to get a token, should raise InvalidParamsError because the code has expired
        with pytest.raises(InvalidParamsError) as exc_info:
            await client.get_device_token("device_code_123")

        # Verify the error contains information about expired token
        assert "expired_token" in str(exc_info.value.data)

        # Verify the client is not authenticated
        assert client.is_authenticated() is False
