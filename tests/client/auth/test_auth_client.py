import json
import os
import threading
import time
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest
from _pytest.logging import LogCaptureFixture

from client.auth import AuthClient
from models.auth import TraktAuthToken, TraktDeviceCode
from utils.api.error_types import TraktResourceNotFoundError
from utils.api.errors import handle_api_errors_func


@pytest.mark.asyncio
async def test_auth_client_init_with_credentials(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    client = AuthClient()
    assert client.client_id == "test_id"
    assert client.client_secret == "test_secret"
    assert "trakt-api-key" in client.headers
    assert client.headers["trakt-api-key"] == "test_id"


@pytest.mark.asyncio
async def test_auth_client_init_without_credentials(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TRAKT_CLIENT_ID", "")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "")

    with pytest.raises(ValueError, match="Trakt API credentials not found"):
        AuthClient()


@pytest.mark.asyncio
async def test_auth_client_load_auth_token_success(monkeypatch: pytest.MonkeyPatch):
    mock_token_data = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 7200,
        "created_at": int(time.time()),
        "scope": "public",
        "token_type": "bearer",
    }

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with (
        patch("dotenv.load_dotenv"),
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_token_data))),
    ):
        client = AuthClient()

        assert client.auth_token is not None
        assert client.auth_token.access_token == "test_access_token"
        assert client.auth_token.refresh_token == "test_refresh_token"
        assert client.is_authenticated() is True


@pytest.mark.asyncio
async def test_auth_client_load_auth_token_file_not_exists(
    monkeypatch: pytest.MonkeyPatch,
):
    def path_exists_side_effect(path: str) -> bool:
        return path != "auth_token.json"

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with (
        patch("dotenv.load_dotenv"),
        patch("os.path.exists", side_effect=path_exists_side_effect),
    ):
        client = AuthClient()
        assert client.auth_token is None
        assert client.is_authenticated() is False


@pytest.mark.asyncio
async def test_auth_client_is_authenticated_with_valid_token(
    monkeypatch: pytest.MonkeyPatch,
):
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with patch("dotenv.load_dotenv"):
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
async def test_auth_client_is_authenticated_with_expired_token(
    monkeypatch: pytest.MonkeyPatch,
):
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with patch("dotenv.load_dotenv"):
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
async def test_auth_client_get_device_code(monkeypatch: pytest.MonkeyPatch):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "device_code": "device_code_123",
        "user_code": "USER123",
        "verification_url": "https://trakt.tv/activate",
        "expires_in": 600,
        "interval": 5,
    }
    mock_response.raise_for_status = MagicMock()

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with patch("httpx.AsyncClient") as mock_client:
        # Mock async methods for new shared client pattern
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_response)
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = AuthClient()
        result = await client.get_device_code()

        # Result is a TraktDeviceCode Pydantic model
        assert isinstance(result, TraktDeviceCode)
        assert result.device_code == "device_code_123"
        assert result.user_code == "USER123"


@pytest.mark.asyncio
async def test_auth_client_get_device_token_success(monkeypatch: pytest.MonkeyPatch):
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

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch("dotenv.load_dotenv"),
        patch("os.open") as mock_os_open,
        patch("os.fdopen") as mock_fdopen,
        patch("os.replace") as mock_replace,
    ):
        # Create mock instance with async methods
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_response)
        mock_instance.get = AsyncMock()
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        # Set up the os.open and os.fdopen mocks
        mock_fd = 3
        mock_os_open.return_value = mock_fd
        mock_file_obj = MagicMock()
        mock_fdopen.return_value = mock_file_obj
        mock_fdopen.return_value.__enter__ = mock_file_obj
        mock_fdopen.return_value.__exit__ = MagicMock(return_value=None)

        client = AuthClient()
        result = await client.get_device_token("device_code_123")

        # Result is a TraktAuthToken
        assert isinstance(result, TraktAuthToken)
        assert result.access_token == "access_token_123"
        assert result.refresh_token == "refresh_token_123"

        # Verify that os.open was called with secure permissions on temp file
        mock_os_open.assert_called_once_with(
            "auth_token.json.tmp", os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600
        )
        # Verify atomic replace was called
        mock_replace.assert_called_once_with("auth_token.json.tmp", "auth_token.json")
        # Verify that file write was called
        assert mock_fdopen.return_value.write.called
        # Optionally assert that JSON was written at least once
        mock_fdopen.return_value.write.assert_called()


def test_clear_auth_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with (
        patch("dotenv.load_dotenv"),
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
        # Ensure Authorization header is present before clearing
        client.headers["Authorization"] = f"Bearer {client.auth_token.access_token}"

        result = client.clear_auth_token()

        assert result is True
        assert client.auth_token is None
        assert "Authorization" not in client.headers
        mock_remove.assert_called_once_with("auth_token.json")


def test_clear_auth_token_no_file(monkeypatch: pytest.MonkeyPatch):
    def path_exists_side_effect(path: str) -> bool:
        # Only return False for auth_token.json
        return path != "auth_token.json"

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with (
        patch("dotenv.load_dotenv"),
        patch("os.path.exists", side_effect=path_exists_side_effect),
    ):
        client = AuthClient()
        result = client.clear_auth_token()

        assert result is False
        assert client.auth_token is None


def test_clear_auth_token_remove_error_returns_true(
    monkeypatch: pytest.MonkeyPatch, caplog: LogCaptureFixture
) -> None:
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with patch("dotenv.load_dotenv"):
        client = AuthClient()

    client.auth_token = TraktAuthToken(
        access_token="test_token",
        refresh_token="test_refresh",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )

    with patch("os.remove", side_effect=OSError("Permission denied")):
        result = client.clear_auth_token()

    assert result is True
    # In-memory state should be cleared even when file deletion fails
    assert client.auth_token is None
    assert "Authorization" not in client.headers
    # Check that the warning message was logged
    assert "Failed to remove auth token file" in caplog.text
    assert "Permission denied" in caplog.text


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
    assert exc_info.value.data is not None
    assert exc_info.value.data.get("http_status") == 404
    assert exc_info.value.code == -32600


def test_clear_auth_token_concurrent_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that concurrent clear_auth_token calls are thread-safe.

    Only one call should actually clear the token; others should return False.
    """
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    remove_call_count = 0
    remove_lock = threading.Lock()

    def mock_remove(path: str) -> None:
        nonlocal remove_call_count
        with remove_lock:
            remove_call_count += 1
        # Simulate some I/O delay to increase chance of race
        time.sleep(0.01)

    with patch("dotenv.load_dotenv"):
        client = AuthClient()

    client.auth_token = TraktAuthToken(
        access_token="test_token",
        refresh_token="test_refresh",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )
    client.headers["Authorization"] = f"Bearer {client.auth_token.access_token}"

    results: list[bool] = []
    results_lock = threading.Lock()

    def call_clear() -> None:
        result = client.clear_auth_token()
        with results_lock:
            results.append(result)

    with patch("os.remove", side_effect=mock_remove):
        # Launch multiple threads to call clear_auth_token concurrently
        threads = [threading.Thread(target=call_clear) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    # Only one call should return True (actually cleared)
    assert results.count(True) == 1
    # Others should return False (already cleared)
    assert results.count(False) == 4
    # File removal should only be called once
    assert remove_call_count == 1
    # Token should be cleared
    assert client.auth_token is None


def test_clear_auth_token_already_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that clear_auth_token returns False when token is already None."""
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    def path_exists_side_effect(path: str) -> bool:
        # Return False for auth_token.json to skip loading
        return path != "auth_token.json"

    with (
        patch("dotenv.load_dotenv"),
        patch("os.path.exists", side_effect=path_exists_side_effect),
        patch("os.remove") as mock_remove,
    ):
        client = AuthClient()
        # auth_token is already None from init
        assert client.auth_token is None

        result = client.clear_auth_token()

        assert result is False
        # os.remove should never be called
        mock_remove.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that refresh_access_token exchanges refresh token for new access token."""
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    new_token_data = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 86400,
        "created_at": current_time,
        "scope": "public",
        "token_type": "bearer",
    }

    mock_response = MagicMock()
    mock_response.json.return_value = new_token_data
    mock_response.raise_for_status = MagicMock()

    with (
        patch("dotenv.load_dotenv"),
        patch("httpx.AsyncClient") as mock_client,
        patch("os.open") as mock_os_open,
        patch("os.fdopen") as mock_fdopen,
        patch("os.replace"),
    ):
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_response)
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        mock_os_open.return_value = 3
        mock_file_obj = MagicMock()
        mock_fdopen.return_value = mock_file_obj
        mock_fdopen.return_value.__enter__ = mock_file_obj
        mock_fdopen.return_value.__exit__ = MagicMock(return_value=None)

        client = AuthClient()
        # Set an expired token with a refresh token
        client.auth_token = TraktAuthToken(
            access_token="old_access_token",
            refresh_token="old_refresh_token",
            expires_in=3600,
            created_at=current_time - 4000,
            scope="public",
            token_type="bearer",
        )

        result = await client.refresh_access_token()

        assert result is True
        assert client.auth_token is not None
        assert client.auth_token.access_token == "new_access_token"
        assert client.auth_token.refresh_token == "new_refresh_token"
        assert client.headers["Authorization"] == "Bearer new_access_token"


@pytest.mark.asyncio
async def test_refresh_access_token_auth_failure_clears_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that permanent auth failure (401) clears the stale token."""
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"error": "invalid_grant"}

    with (
        patch("dotenv.load_dotenv"),
        patch("httpx.AsyncClient") as mock_client,
        patch("os.remove"),
    ):
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(
            return_value=MagicMock(
                raise_for_status=MagicMock(
                    side_effect=httpx.HTTPStatusError(
                        "Unauthorized",
                        request=MagicMock(),
                        response=mock_response,
                    )
                ),
                json=MagicMock(return_value={"error": "invalid_grant"}),
            )
        )
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="old_access_token",
            refresh_token="old_refresh_token",
            expires_in=3600,
            created_at=current_time - 4000,
            scope="public",
            token_type="bearer",
        )

        result = await client.refresh_access_token()

        assert result is False
        assert client.auth_token is None


@pytest.mark.asyncio
async def test_refresh_access_token_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that refresh returns False when no token exists."""
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with patch("dotenv.load_dotenv"):
        client = AuthClient()
        client.auth_token = None

        result = await client.refresh_access_token()

        assert result is False


@pytest.mark.asyncio
async def test_refresh_access_token_network_error_preserves_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that transient network errors do NOT clear the refresh token."""
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with (
        patch("dotenv.load_dotenv"),
        patch("httpx.AsyncClient") as mock_client,
    ):
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="old_access_token",
            refresh_token="old_refresh_token",
            expires_in=3600,
            created_at=current_time - 4000,
            scope="public",
            token_type="bearer",
        )

        result = await client.refresh_access_token()

        assert result is False
        # Token must be preserved for next retry
        assert client.auth_token is not None
        assert client.auth_token.refresh_token == "old_refresh_token"


@pytest.mark.asyncio
async def test_refresh_access_token_invalid_grant_clears_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that a 400 invalid_grant response clears the token."""
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "invalid_grant"}

    with (
        patch("dotenv.load_dotenv"),
        patch("httpx.AsyncClient") as mock_client,
        patch("os.remove"),
    ):
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(
            return_value=MagicMock(
                raise_for_status=MagicMock(
                    side_effect=httpx.HTTPStatusError(
                        "Bad Request",
                        request=MagicMock(),
                        response=mock_response,
                    )
                ),
                json=MagicMock(return_value={"error": "invalid_grant"}),
            )
        )
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="old_access_token",
            refresh_token="old_refresh_token",
            expires_in=3600,
            created_at=current_time - 4000,
            scope="public",
            token_type="bearer",
        )

        result = await client.refresh_access_token()

        assert result is False
        assert client.auth_token is None


@pytest.mark.asyncio
async def test_ensure_authenticated_valid_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test ensure_authenticated returns True for valid token."""
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with patch("dotenv.load_dotenv"):
        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="valid_token",
            refresh_token="refresh_token",
            expires_in=7200,
            created_at=current_time,
            scope="public",
            token_type="bearer",
        )

        result = await client.ensure_authenticated()

        assert result is True
        # Token should be unchanged (no refresh happened)
        assert client.auth_token.access_token == "valid_token"


@pytest.mark.asyncio
async def test_ensure_authenticated_expired_token_refreshes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that ensure_authenticated refreshes expired token."""
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    new_token_data = {
        "access_token": "refreshed_token",
        "refresh_token": "new_refresh",
        "expires_in": 86400,
        "created_at": current_time,
        "scope": "public",
        "token_type": "bearer",
    }

    mock_response = MagicMock()
    mock_response.json.return_value = new_token_data
    mock_response.raise_for_status = MagicMock()

    with (
        patch("dotenv.load_dotenv"),
        patch("httpx.AsyncClient") as mock_client,
        patch("os.open") as mock_os_open,
        patch("os.fdopen") as mock_fdopen,
        patch("os.replace"),
    ):
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_response)
        mock_instance.aclose = AsyncMock()
        mock_client.return_value = mock_instance

        mock_os_open.return_value = 3
        mock_file_obj = MagicMock()
        mock_fdopen.return_value = mock_file_obj
        mock_fdopen.return_value.__enter__ = mock_file_obj
        mock_fdopen.return_value.__exit__ = MagicMock(return_value=None)

        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="expired_token",
            refresh_token="old_refresh",
            expires_in=3600,
            created_at=current_time - 4000,
            scope="public",
            token_type="bearer",
        )

        result = await client.ensure_authenticated()

        assert result is True
        assert client.auth_token is not None
        assert client.auth_token.access_token == "refreshed_token"


@pytest.mark.asyncio
async def test_ensure_authenticated_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ensure_authenticated returns False when no token exists."""
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with patch("dotenv.load_dotenv"):
        client = AuthClient()
        client.auth_token = None

        result = await client.ensure_authenticated()

        assert result is False


@pytest.mark.asyncio
async def test_ensure_authenticated_expired_no_refresh_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that ensure_authenticated returns False when token is expired but has no
    refresh token.
    """
    current_time = int(time.time())

    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    with patch("dotenv.load_dotenv"):
        client = AuthClient()
        client.auth_token = TraktAuthToken(
            access_token="expired_token",
            refresh_token="",
            expires_in=3600,
            created_at=current_time - 4000,
            scope="public",
            token_type="bearer",
        )

        result = await client.ensure_authenticated()

        assert result is False
        # Token should be unchanged (no refresh attempted)
        assert client.auth_token is not None
        assert client.auth_token.access_token == "expired_token"


def test_clear_auth_token_file_deleted_externally(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that clear_auth_token clears memory state even if file doesn't exist.

    This handles the case where the auth file was deleted externally but the
    token is still in memory.
    """
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    # First, create the client normally (file doesn't exist during init)
    with patch("dotenv.load_dotenv"):
        client = AuthClient()

    # Manually set token to simulate it being set in memory without file
    # (e.g., token was saved, then file was deleted externally)
    client.auth_token = TraktAuthToken(
        access_token="test_token",
        refresh_token="test_refresh",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )
    client.headers["Authorization"] = f"Bearer {client.auth_token.access_token}"

    # Now call clear_auth_token with file not existing (deleted externally)
    # os.remove raises FileNotFoundError, which is suppressed
    with patch("os.remove", side_effect=FileNotFoundError):
        result = client.clear_auth_token()

    # Should return True because we cleared the memory state
    assert result is True
    # Token should be cleared from memory
    assert client.auth_token is None
    # Authorization header should be removed
    assert "Authorization" not in client.headers
