import json
import os
import time
from unittest.mock import MagicMock, mock_open, patch

import httpx
import pytest

from client.auth import AuthClient
from models.auth import TraktAuthToken
from utils.api.error_types import TraktResourceNotFoundError
from utils.api.errors import handle_api_errors_func


@pytest.mark.asyncio
async def test_auth_client_init_with_credentials():
    with patch.dict(
        os.environ, {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"}
    ):
        client = AuthClient()
        assert client.client_id == "test_id"
        assert client.client_secret == "test_secret"
        assert "trakt-api-key" in client.headers
        assert client.headers["trakt-api-key"] == "test_id"


@pytest.mark.asyncio
async def test_auth_client_init_without_credentials():
    with (
        patch.dict(os.environ, {"TRAKT_CLIENT_ID": "", "TRAKT_CLIENT_SECRET": ""}),
        pytest.raises(ValueError, match="Trakt API credentials not found"),
    ):
        AuthClient()


@pytest.mark.asyncio
async def test_auth_client_load_auth_token_success():
    mock_token_data = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 7200,
        "created_at": int(time.time()),
        "scope": "public",
        "token_type": "bearer",
    }

    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_token_data))),
    ):
        client = AuthClient()

        assert client.auth_token is not None
        assert client.auth_token.access_token == "test_access_token"
        assert client.auth_token.refresh_token == "test_refresh_token"
        assert client.is_authenticated() is True


@pytest.mark.asyncio
async def test_auth_client_load_auth_token_file_not_exists():
    def path_exists_side_effect(path: str) -> bool:
        return path != "auth_token.json"

    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
        patch("os.path.exists", side_effect=path_exists_side_effect),
    ):
        client = AuthClient()
        assert client.auth_token is None
        assert client.is_authenticated() is False


@pytest.mark.asyncio
async def test_auth_client_is_authenticated_with_valid_token():
    current_time = int(time.time())

    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=current_time,
            scope="public",
            token_type="bearer",
        )

        assert client.is_authenticated() is True


@pytest.mark.asyncio
async def test_auth_client_is_authenticated_with_expired_token():
    current_time = int(time.time())

    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=3600,
            created_at=current_time
            - 4000,  # Token created 4000 seconds ago, expires in 3600
            scope="public",
            token_type="bearer",
        )

        assert client.is_authenticated() is False


@pytest.mark.asyncio
async def test_auth_client_get_device_code():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "device_code": "device_code_123",
        "user_code": "USER123",
        "verification_url": "https://trakt.tv/activate",
        "expires_in": 600,
        "interval": 5,
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        client = AuthClient()
        result = await client.get_device_code()

        # Result is a dict (DeviceCodeResponse TypedDict)
        assert isinstance(result, dict)
        assert result["device_code"] == "device_code_123"
        assert result["user_code"] == "USER123"


@pytest.mark.asyncio
async def test_auth_client_get_device_token_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "access_token": "access_token_123",
        "refresh_token": "refresh_token_123",
        "expires_in": 7200,
        "created_at": 1600000000,
        "scope": "public",
        "token_type": "bearer",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("dotenv.load_dotenv"),
        patch("builtins.open", mock_open()) as mock_file,
        patch("json.dumps", return_value="{}") as mock_json_dumps,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        client = AuthClient()
        result = await client.get_device_token("device_code_123")

        # Result is a TraktAuthToken
        assert isinstance(result, TraktAuthToken)
        assert result.access_token == "access_token_123"
        assert result.refresh_token == "refresh_token_123"

        assert mock_file.called
        # Verify that json.dumps was called with the auth token data (should be the last call)
        calls = mock_json_dumps.call_args_list
        auth_token_call = calls[-1]
        assert "access_token" in str(auth_token_call)


def test_clear_auth_token():
    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
        patch("os.path.exists", return_value=True),
        patch("os.remove") as mock_remove,
    ):
        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        result = client.clear_auth_token()

        assert result is True
        assert client.auth_token is None
        mock_remove.assert_called_once_with("auth_token.json")


def test_clear_auth_token_no_file():
    def path_exists_side_effect(path: str) -> bool:
        # Only return False for auth_token.json
        return path != "auth_token.json"

    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
        patch("os.path.exists", side_effect=path_exists_side_effect),
    ):
        client = AuthClient()
        result = client.clear_auth_token()

        assert result is False
        assert client.auth_token is None


def test_clear_auth_token_remove_error():
    # Use a list to track call count (mutable in closure)
    call_count = [0]

    def path_exists_side_effect(path: str) -> bool:
        # Return False for auth_token.json during init to avoid loading
        # Return True for auth_token.json during clear_auth_token
        call_count[0] += 1

        # First call is during init, return False to skip loading
        # Second call is during clear_auth_token, return True
        if path == "auth_token.json":
            return call_count[0] > 1
        return True

    with (
        patch("dotenv.load_dotenv"),
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
        patch("os.path.exists", side_effect=path_exists_side_effect),
        patch("os.remove", side_effect=OSError("Permission denied")),
        patch("builtins.print") as mock_print,
    ):
        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=7200,
            created_at=int(time.time()),
            scope="public",
            token_type="bearer",
        )

        result = client.clear_auth_token()

        assert result is False
        # Token should remain unchanged on error
        assert client.auth_token is not None
        # Check that the error message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any(
            "Error clearing auth token: Permission denied" in call
            for call in print_calls
        )


@pytest.mark.asyncio
async def test_handle_api_errors_decorator():
    # Create a test function that will raise an exception
    @handle_api_errors_func
    async def test_func():
        raise httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )

    # The decorator should catch the exception and raise an MCP error
    with pytest.raises(TraktResourceNotFoundError) as exc_info:
        await test_func()

    assert "The requested resource 'unknown' was not found" in exc_info.value.message
