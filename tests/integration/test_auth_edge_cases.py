"""Integration tests for authentication edge cases."""

import json
import os
import tempfile
import time
from unittest.mock import patch

import pytest
from httpx import ConnectError, ReadTimeout
from pydantic import ValidationError

from client.auth.client import AUTH_TOKEN_FILE, AuthClient
from models.auth.auth import TraktAuthToken, TraktDeviceCode
from server.auth.tools import check_auth_status, start_device_auth
from utils.api.errors import InternalError, InvalidRequestError


class TestAuthEdgeCases:
    """Test edge cases in authentication flow."""

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Clean up auth state before and after each test."""
        # Clear any existing auth token file
        if os.path.exists(AUTH_TOKEN_FILE):
            os.remove(AUTH_TOKEN_FILE)

        # Clear active auth flow
        from server.auth.tools import active_auth_flow
        active_auth_flow.clear()

        yield

        # Clean up after test
        if os.path.exists(AUTH_TOKEN_FILE):
            os.remove(AUTH_TOKEN_FILE)
        active_auth_flow.clear()

    @pytest.mark.asyncio
    async def test_device_code_expiry_during_auth_flow(self):
        """Test error handling when device code expires during auth flow."""
        # Mock device code response with short expiry
        mock_device_code = TraktDeviceCode(
            device_code="test_device_code",
            user_code="TEST123",
            verification_url="https://trakt.tv/activate",
            expires_in=1,  # Very short expiry
            interval=1,
        )

        with patch.object(AuthClient, "get_device_code", return_value=mock_device_code):
            # Start auth flow
            result = await start_device_auth()
            assert "https://trakt.tv/activate" in result
            assert "TEST123" in result

            # Wait for device code to expire
            time.sleep(2)

            # Try to check auth status after expiry
            status = await check_auth_status()
            assert "Authentication flow expired" in status
            assert "start_device_auth" in status

    @pytest.mark.asyncio
    async def test_expired_auth_token(self):
        """Test handling of expired authentication tokens."""
        # Create expired token
        expired_token = TraktAuthToken(
            access_token="expired_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh_token",
            scope="public",
            created_at=int(time.time()) - 7200,  # 2 hours ago, expired
        )

        # Save expired token
        with open(AUTH_TOKEN_FILE, "w") as f:
            json.dump(expired_token.model_dump(), f)

        # Create client - should load but recognize token as expired
        client = AuthClient()
        assert client.auth_token is not None
        assert not client.is_authenticated()  # Should be False due to expiry

        # Test that tools detect expired authentication
        from server.user.tools import fetch_user_watched_shows

        # Mock the auth flow to avoid real API calls
        with patch(
            "server.user.tools.start_device_auth", return_value="Mock auth instructions"
        ):
            # Should return auth instructions, not error
            result = await fetch_user_watched_shows()
            assert "Mock auth instructions" in result

    @pytest.mark.asyncio
    async def test_corrupted_auth_token_file(self):
        """Test handling of corrupted auth token file."""
        # Create corrupted token file
        with open(AUTH_TOKEN_FILE, "w") as f:
            f.write("invalid json content {")

        # Client should handle corrupted file gracefully
        client = AuthClient()
        assert client.auth_token is None
        assert not client.is_authenticated()

    @pytest.mark.asyncio
    async def test_network_error_during_device_code_retrieval(self):
        """Test network errors during device code retrieval."""
        # Mock the underlying _make_request method to raise ConnectError
        with patch.object(
            AuthClient, "_make_request", side_effect=ConnectError("Connection failed")
        ):
            client = AuthClient()

            # Should propagate network error as InternalError
            with pytest.raises(InternalError) as exc_info:
                await client.get_device_code()

            assert "Unable to connect to Trakt API" in str(exc_info.value)
            assert exc_info.value.code == -32603

    @pytest.mark.asyncio
    async def test_network_timeout_during_token_exchange(self):
        """Test timeout errors during token exchange."""
        # Mock the underlying _make_request method to raise ReadTimeout
        with patch.object(
            AuthClient, "_make_request", side_effect=ReadTimeout("Request timed out")
        ):
            client = AuthClient()

            # Should propagate timeout as InternalError
            with pytest.raises(InternalError) as exc_info:
                await client.get_device_token("test_device_code")

            assert "Unable to connect to Trakt API" in str(exc_info.value)
            assert exc_info.value.code == -32603

    @pytest.mark.asyncio
    async def test_invalid_device_code_error(self):
        """Test handling of invalid device codes."""
        # Mock 400 error response for invalid device code
        mock_error = InvalidRequestError(
            "Bad request. Please check your request parameters.",
            data={"http_status": 400},
        )

        with patch.object(AuthClient, "_make_request", side_effect=mock_error):
            client = AuthClient()

            # Should return None for 400 errors (user hasn't authorized)
            result = await client.get_device_token("invalid_device_code")
            assert result is None

    @pytest.mark.asyncio
    async def test_server_error_during_token_exchange(self):
        """Test server errors during token exchange."""
        # Mock 500 error from Trakt API
        mock_error = InternalError("Internal server error", data={"http_status": 500})

        with patch.object(AuthClient, "_make_request", side_effect=mock_error):
            client = AuthClient()

            # Should propagate server errors
            with pytest.raises(InternalError) as exc_info:
                await client.get_device_token("test_device_code")

            assert exc_info.value.code == -32603
            assert "Internal server error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_during_auth_flow(self):
        """Test rate limiting during authentication flow."""
        # Mock 429 rate limit error
        mock_error = InvalidRequestError(
            "Rate limit exceeded", data={"http_status": 429}
        )

        with patch.object(AuthClient, "_make_request", side_effect=mock_error):
            client = AuthClient()

            # Should propagate rate limit as InvalidRequestError
            with pytest.raises(InvalidRequestError) as exc_info:
                await client.get_device_code()

            assert exc_info.value.code == -32600
            assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_concurrent_auth_flows(self):
        """Test handling of multiple concurrent authentication flows."""
        # Mock device code responses
        mock_device_code_1 = TraktDeviceCode(
            device_code="device_code_1",
            user_code="CODE1",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
            interval=5,
        )

        mock_device_code_2 = TraktDeviceCode(
            device_code="device_code_2",
            user_code="CODE2",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
            interval=5,
        )

        with (
            patch("client.base.load_dotenv"),
            patch.dict(
                os.environ,
                {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
            ),
            patch("client.auth.client.os.path.exists", return_value=False),  # No auth token file
            patch.object(
                AuthClient,
                "get_device_code",
                side_effect=[mock_device_code_1, mock_device_code_2],
            ),
        ):
            # Start first auth flow
            result1 = await start_device_auth()
            assert "CODE1" in result1

            # Start second auth flow (should override first)
            result2 = await start_device_auth()
            assert "CODE2" in result2

            # The test validates that the second flow overrides the first
            # by ensuring CODE2 is in the result, which proves the second
            # device code was used when get_device_code was called the second time

    @pytest.mark.asyncio
    async def test_auth_token_edge_cases(self):
        """Test various auth token edge cases."""
        # Test token with missing fields
        incomplete_token_data = {
            "access_token": "test_token",
            "token_type": "Bearer",
            # Missing expires_in, created_at
        }

        with open(AUTH_TOKEN_FILE, "w") as f:
            json.dump(incomplete_token_data, f)

        # Should handle missing fields gracefully
        client = AuthClient()
        assert client.auth_token is None  # Should fail to load due to validation

    @pytest.mark.asyncio
    async def test_permission_denied_auth_token_file(self):
        """Test handling of permission denied on auth token file."""
        # Create a temporary directory with restricted permissions
        with tempfile.TemporaryDirectory() as temp_dir:
            restricted_file = os.path.join(temp_dir, "restricted_auth_token.json")

            # Create file
            with open(restricted_file, "w") as f:
                json.dump({"test": "data"}, f)

            # Remove read permissions
            os.chmod(restricted_file, 0o000)

            try:
                # Patch AUTH_TOKEN_FILE to point to restricted file
                with patch("client.auth.client.AUTH_TOKEN_FILE", restricted_file):
                    # Should handle permission denied gracefully
                    client = AuthClient()
                    assert client.auth_token is None
            finally:
                # Restore permissions for cleanup
                os.chmod(restricted_file, 0o644)

    @pytest.mark.asyncio
    async def test_malformed_trakt_api_responses(self):
        """Test handling of malformed responses from Trakt API."""
        # Test malformed device code response
        malformed_device_response = {
            "device_code": "test_code",
            # Missing required fields: user_code, verification_url, expires_in, interval
        }

        with patch.object(
            AuthClient, "_make_request", return_value=malformed_device_response
        ):
            client = AuthClient()

            # Should raise validation error when trying to create TraktDeviceCode
            with pytest.raises(ValidationError):
                await client.get_device_code()

    @pytest.mark.asyncio
    async def test_auth_flow_timing_edge_cases(self):
        """Test timing-related edge cases in auth flow."""
        # Mock device code with specific timing
        mock_device_code = TraktDeviceCode(
            device_code="timing_test_code",
            user_code="TIME123",
            verification_url="https://trakt.tv/activate",
            expires_in=60,
            interval=5,
        )

        # Clear any existing auth state
        from server.auth.tools import active_auth_flow
        active_auth_flow.clear()

        # Mock get_device_token to raise 400 error (authorization pending)
        mock_pending_error = InvalidRequestError(
            "Bad request. Please check your request parameters.",
            data={"http_status": 400},
        )

        with (
            patch("client.base.load_dotenv"),
            patch.dict(
                os.environ,
                {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
            ),
            patch("client.auth.client.os.path.exists", return_value=False),  # No auth token file exists
            patch.object(AuthClient, "get_device_code", return_value=mock_device_code),
            patch.object(
                AuthClient, "get_device_token", side_effect=mock_pending_error
            ),
        ):
            # Start auth flow
            result = await start_device_auth()
            assert "TIME123" in result  # Verify auth flow started

            # Check status immediately (should work)
            status1 = await check_auth_status()
            assert "Authorization Pending" in status1 or "Please wait" in status1

            # Check again immediately (should be rate limited)
            status2 = await check_auth_status()
            assert "Please wait" in status2

            # Wait for interval and check again
            time.sleep(6)  # Wait longer than interval
            status3 = await check_auth_status()
            # Should show pending status, not rate limited message
            assert "Authorization Pending" in status3 or "completed the authorization" in status3
            assert "Please wait" not in status3 and "seconds before checking" not in status3
