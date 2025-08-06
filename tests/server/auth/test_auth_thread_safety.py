"""Test thread-safety of auth flow operations."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from server.auth.tools import check_auth_status, start_device_auth
from utils.api.error_types import AuthorizationPendingError


class TestAuthFlowThreadSafety:
    """Test thread-safety of authentication flow operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_auth_flow(self) -> None:
        """Reset auth flow before each test."""
        from server.auth.tools import active_auth_flow, auth_flow_lock

        # Clear the dictionary with proper locking
        async with auth_flow_lock:
            for key in list(active_auth_flow.keys()):
                del active_auth_flow[key]

    @pytest.mark.asyncio
    async def test_concurrent_auth_flow_starts(self) -> None:
        """Test multiple concurrent start_device_auth calls."""
        mock_client = MagicMock()
        mock_client.is_authenticated.return_value = False

        # Different device codes for each call
        device_responses = [
            {
                "device_code": f"device_{i}",
                "user_code": f"USER{i:03d}",
                "verification_url": "https://trakt.tv/activate",
                "expires_in": 600,
                "interval": 5,
            }
            for i in range(10)
        ]

        # Set up mock to return different responses
        mock_client.get_device_code = AsyncMock(side_effect=device_responses)

        with patch("server.auth.tools.AuthClient", return_value=mock_client):
            # Start multiple auth flows concurrently
            tasks = [start_device_auth() for _ in range(10)]
            results = await asyncio.gather(*tasks)

            # All should succeed
            assert all("Trakt Authentication Required" in result for result in results)

            # The last auth flow should win
            from server.auth.tools import active_auth_flow, auth_flow_lock

            async with auth_flow_lock:
                assert active_auth_flow.get("device_code") in [
                    f"device_{i}" for i in range(10)
                ]

    @pytest.mark.asyncio
    async def test_concurrent_auth_status_checks(self) -> None:
        """Test multiple concurrent check_auth_status calls."""
        from server.auth.tools import active_auth_flow, auth_flow_lock

        # Set up an active auth flow
        async with auth_flow_lock:
            active_auth_flow.update(
                {
                    "device_code": "test_device",
                    "expires_at": 999999999999,  # Far future
                    "interval": 5,
                    "last_poll": 0,
                }
            )

        mock_client = MagicMock()
        mock_client.is_authenticated.return_value = False
        mock_client.get_device_token = AsyncMock(
            side_effect=AuthorizationPendingError(device_code="test_device")
        )  # Still pending

        with patch("server.auth.tools.AuthClient", return_value=mock_client):
            # Check status concurrently
            tasks = [check_auth_status() for _ in range(5)]
            results = await asyncio.gather(*tasks)

            # First should succeed, others should wait
            wait_messages = [r for r in results if "wait" in r]
            assert len(wait_messages) >= 1  # At least some should be told to wait

    @pytest.mark.asyncio
    async def test_concurrent_auth_success_race(self) -> None:
        """Test race condition when multiple checks succeed simultaneously."""
        from server.auth.tools import active_auth_flow, auth_flow_lock

        # Set up an active auth flow
        async with auth_flow_lock:
            active_auth_flow.update(
                {
                    "device_code": "test_device",
                    "expires_at": 999999999999,
                    "interval": 0,  # No wait required
                    "last_poll": 0,
                }
            )

        mock_client = MagicMock()

        # Track authentication state
        auth_state = {"authenticated": False}

        def is_authenticated():
            return auth_state["authenticated"]

        mock_client.is_authenticated = is_authenticated

        # Create a token that will be returned
        from models.auth import TraktAuthToken

        mock_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="refresh_token",
            expires_in=3600,
            created_at=1234567890,
            scope="public",
            token_type="bearer",
        )

        # Simulate delayed token response that also sets authenticated state
        async def get_device_token(device_code: str) -> TraktAuthToken:
            await asyncio.sleep(0.01)  # Small delay
            auth_state["authenticated"] = True
            return mock_token

        mock_client.get_device_token = get_device_token

        with patch("server.auth.tools.AuthClient", return_value=mock_client):
            # Multiple concurrent successful auth checks
            tasks = [check_auth_status() for _ in range(5)]
            results = await asyncio.gather(*tasks)

            # At least one should report success
            success_messages = [r for r in results if "Authentication Successful" in r]
            assert len(success_messages) >= 1

            # The test verifies that concurrent access doesn't cause crashes or data corruption
            # Multiple successes are OK - it means multiple coroutines authenticated before flow was cleared
            # This is acceptable behavior as long as no errors occur
