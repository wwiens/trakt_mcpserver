"""Tests for the UserClient."""

import pytest

from client.user import UserClient


@pytest.mark.asyncio
async def test_user_client_init_with_credentials(monkeypatch: pytest.MonkeyPatch):
    """Test UserClient initialization with credentials."""
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    client = UserClient()
    assert client.client_id == "test_id"
    assert client.client_secret == "test_secret"
    assert "trakt-api-key" in client.headers
    assert client.headers["trakt-api-key"] == "test_id"


@pytest.mark.asyncio
async def test_user_client_init_without_credentials(monkeypatch: pytest.MonkeyPatch):
    """Test UserClient initialization without credentials raises error."""
    monkeypatch.setenv("TRAKT_CLIENT_ID", "")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "")

    with pytest.raises(ValueError, match="Trakt API credentials not found"):
        UserClient()


@pytest.mark.asyncio
async def test_user_client_inherits_auth_methods(monkeypatch: pytest.MonkeyPatch):
    """Test that UserClient inherits authentication methods."""
    monkeypatch.setenv("TRAKT_CLIENT_ID", "test_id")
    monkeypatch.setenv("TRAKT_CLIENT_SECRET", "test_secret")

    client = UserClient()
    # UserClient should inherit from AuthClient
    assert hasattr(client, "is_authenticated")
    assert hasattr(client, "get_token_expiry")
    assert hasattr(client, "get_user_watched_shows")
    assert hasattr(client, "get_user_watched_movies")
