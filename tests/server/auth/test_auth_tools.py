import asyncio
import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from models.auth.auth import TraktAuthToken, TraktDeviceCode
from server.auth.tools import check_auth_status, clear_auth, start_device_auth
from utils.api.error_types import AuthorizationPendingError


@pytest.mark.asyncio
async def test_start_device_auth():
    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", {}),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        device_code_model = TraktDeviceCode(
            device_code="device_code_123",
            user_code="USER123",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
            interval=5,
        )

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(device_code_model)
        mock_client.get_device_code.return_value = future

        result = await start_device_auth()

        assert "USER123" in result
        assert "https://trakt.tv/activate" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_code.assert_called_once()


@pytest.mark.asyncio
async def test_start_device_auth_already_authenticated():
    with patch("server.auth.tools.AuthClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        result = await start_device_auth()

        assert "You are already authenticated with Trakt" in result

        mock_client.is_authenticated.assert_called_once()


@pytest.mark.asyncio
async def test_check_auth_status_no_active_flow():
    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", {}),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        result = await check_auth_status()

        assert "No active authentication flow" in result
        assert "start_device_auth" in result

        mock_client.is_authenticated.assert_called_once()


@pytest.mark.asyncio
async def test_check_auth_status_expired_flow():
    expired_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) - 100,  # Expired 100 seconds ago
        "interval": 5,
        "last_poll": 0,
    }

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", expired_flow),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        result = await check_auth_status()

        assert "Authentication flow expired" in result
        assert "start_device_auth" in result

        mock_client.is_authenticated.assert_called_once()


@pytest.mark.asyncio
async def test_check_auth_status_already_authenticated():
    with patch("server.auth.tools.AuthClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True

        result = await check_auth_status()

        assert "Authentication Successful!" in result
        assert "You are now authenticated with Trakt" in result

        mock_client.is_authenticated.assert_called_once()


@pytest.mark.asyncio
async def test_check_auth_status_too_early_to_poll():
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time())
        - 2,  # Last polled 2 seconds ago (less than interval)
    }

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", active_flow),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        result = await check_auth_status()

        assert "Please wait" in result
        assert "seconds before checking again" in result

        mock_client.is_authenticated.assert_called_once()
        # Should not poll the token when it's too early
        mock_client.get_device_token.assert_not_called()


@pytest.mark.asyncio
async def test_check_auth_status_pending_authorization():
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10,  # Last polled 10 seconds ago
    }

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", active_flow),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        # Mock get_device_token to raise AuthorizationPendingError
        mock_client.get_device_token.side_effect = AuthorizationPendingError(
            device_code="device_code_123"
        )

        result = await check_auth_status()

        assert "Authorization Pending" in result
        assert "Visit the Trakt activation page" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")


@pytest.mark.asyncio
async def test_check_auth_status_successful_authorization():
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10,  # Last polled 10 seconds ago
    }

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", active_flow),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        token_future: asyncio.Future[Any] = asyncio.Future()
        token_future.set_result(
            TraktAuthToken(
                access_token="access_token_123",
                token_type="bearer",
                expires_in=7200,
                refresh_token="refresh_token_123",
                scope="public",
                created_at=int(time.time()),
            )
        )
        mock_client.get_device_token.return_value = token_future

        result = await check_auth_status()

        assert "Authentication Successful!" in result
        assert "successfully authorized the Trakt MCP application" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")


@pytest.mark.asyncio
async def test_check_auth_status_internal_error():
    """Test check_auth_status handles InternalError gracefully during polling."""
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10,  # Last polled 10 seconds ago
    }

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", active_flow),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        # Mock get_device_token to raise InternalError
        from utils.api.errors import InternalError

        mock_client.get_device_token.side_effect = InternalError(
            "Server error occurred"
        )

        result = await check_auth_status()

        assert "Authorization Check Failed" in result
        assert "Unable to check authorization status" in result
        assert "server error" in result

        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")


@pytest.mark.asyncio
async def test_clear_auth():
    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", {"device_code": "device_code_123"}),
    ):
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = True

        result = await clear_auth()

        assert "You have been successfully logged out of Trakt" in result

        mock_client.clear_auth_token.assert_called_once()

        from server.auth.tools import active_auth_flow

        assert active_auth_flow == {}


@pytest.mark.asyncio
async def test_clear_auth_not_authenticated():
    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", {}),
    ):
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = False

        result = await clear_auth()

        assert "You were not authenticated with Trakt" in result

        mock_client.clear_auth_token.assert_called_once()
