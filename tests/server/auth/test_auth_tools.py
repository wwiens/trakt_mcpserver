import asyncio
import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from config.auth import STALE_LOGIN_HINT
from models.auth.auth import TraktAuthToken, TraktDeviceCode
from server.auth.tools import check_auth_status, clear_auth, start_device_auth
from utils.api.error_types import AuthorizationPendingError, DeviceAuthorizationError


@pytest.mark.asyncio
async def test_start_device_auth():
    empty_flow: dict[str, object] = {}
    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", empty_flow),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False

        device_code_model = TraktDeviceCode(
            device_code="device_code_123",
            user_code="USER123",
            verification_url="https://auth.trakt.tv/activate",
            expires_in=600,
            interval=5,
        )

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(device_code_model)
        mock_client.get_device_code.return_value = future

        result = await start_device_auth()

        assert "USER123" in result
        assert "https://auth.trakt.tv/activate" in result

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
    empty_flow: dict[str, object] = {}
    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", empty_flow),
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
        assert STALE_LOGIN_HINT in result

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
    empty_flow: dict[str, object] = {}
    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", empty_flow),
    ):
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = False

        result = await clear_auth()

        assert "You were not authenticated with Trakt" in result

        mock_client.clear_auth_token.assert_called_once()


def _active_flow() -> dict[str, Any]:
    return {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,
        "interval": 5,
        "last_poll": int(time.time()) - 10,
    }


@pytest.mark.asyncio
async def test_check_auth_status_denied_clears_flow():
    """A denied code ends the flow and shows Trakt's reason."""
    import server.auth.tools as auth_tools

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", _active_flow()),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        mock_client.get_device_token.side_effect = DeviceAuthorizationError(
            http_status=418,
            message="Trakt denied this device code.",
            restart_required=True,
        )

        result = await check_auth_status()

        assert "Authorization Not Completed" in result
        assert "Trakt denied this device code." in result
        assert auth_tools.active_auth_flow == {}


@pytest.mark.asyncio
async def test_check_auth_status_slow_down_keeps_flow():
    """Slow-down keeps the flow so the user can check again with the same code."""
    import server.auth.tools as auth_tools

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", _active_flow()),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        mock_client.get_device_token.side_effect = DeviceAuthorizationError(
            http_status=429, message="Slow down.", restart_required=False
        )

        result = await check_auth_status()

        assert "Slow down." in result
        assert "Wait 10 seconds" in result
        assert auth_tools.active_auth_flow["device_code"] == "device_code_123"
        assert auth_tools.active_auth_flow["interval"] == 10


@pytest.mark.asyncio
async def test_check_auth_status_slow_down_honours_longer_retry_after():
    import server.auth.tools as auth_tools

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", _active_flow()),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        mock_client.get_device_token.side_effect = DeviceAuthorizationError(
            http_status=429,
            message="Slow down.",
            restart_required=False,
            retry_after=30,
        )

        result = await check_auth_status()

        assert "Wait 30 seconds" in result
        assert auth_tools.active_auth_flow["interval"] == 30


@pytest.mark.asyncio
async def test_check_auth_status_already_used_code_but_token_saved():
    """An overlapping check that already saved the token reports success."""
    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", _active_flow()),
    ):
        mock_client = mock_client_class.return_value
        # First check: not yet authenticated. After the 409: token on disk.
        mock_client.is_authenticated.side_effect = [False, True]
        mock_client.get_device_token.side_effect = DeviceAuthorizationError(
            http_status=409, message="Already used.", restart_required=True
        )

        result = await check_auth_status()

        assert "Authentication Successful!" in result
        assert "Already used." not in result


@pytest.mark.asyncio
async def test_check_auth_status_stale_reply_keeps_newer_flow():
    """A late 410 for an old code must not erase a flow started meanwhile."""
    import server.auth.tools as auth_tools

    newer_flow = {**_active_flow(), "device_code": "newer_code"}

    async def _expire_after_new_flow_started(_device_code: str) -> None:
        auth_tools.active_auth_flow = newer_flow
        raise DeviceAuthorizationError(
            http_status=410, message="Expired.", restart_required=True
        )

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", _active_flow()),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        mock_client.get_device_token.side_effect = _expire_after_new_flow_started

        result = await check_auth_status()

        assert "Expired." in result
        assert auth_tools.active_auth_flow["device_code"] == "newer_code"


@pytest.mark.asyncio
async def test_start_device_auth_when_authenticated_points_to_clear_auth():
    """A locally valid token Trakt rejects must not leave the user stuck."""
    with patch("server.auth.tools.AuthClient") as mock_client_class:
        mock_client_class.return_value.is_authenticated.return_value = True

        result = await start_device_auth()

    assert "already authenticated" in result
    assert "`clear_auth`" in result


@pytest.mark.asyncio
async def test_check_auth_status_late_success_keeps_newer_flow():
    """A slow success for an old code must not erase a flow started meanwhile."""
    import server.auth.tools as auth_tools

    newer_flow = {**_active_flow(), "device_code": "newer_code"}

    async def _succeed_after_new_flow_started(_device_code: str) -> None:
        auth_tools.active_auth_flow = newer_flow

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", _active_flow()),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        mock_client.get_device_token.side_effect = _succeed_after_new_flow_started

        result = await check_auth_status()

        assert "Authentication Successful!" in result
        assert auth_tools.active_auth_flow["device_code"] == "newer_code"


@pytest.mark.asyncio
async def test_check_auth_status_unexpected_reply_keeps_interval():
    """Only Trakt's slow-down reply lengthens polling, not e.g. a proxy page."""
    import server.auth.tools as auth_tools

    with (
        patch("server.auth.tools.AuthClient") as mock_client_class,
        patch("server.auth.tools.active_auth_flow", _active_flow()),
    ):
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        mock_client.get_device_token.side_effect = DeviceAuthorizationError(
            http_status=400, message="Unexpected reply.", restart_required=False
        )

        result = await check_auth_status()

        assert "Unexpected reply." in result
        assert auth_tools.active_auth_flow["interval"] == 5
