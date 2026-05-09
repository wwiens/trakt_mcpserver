"""Shared fixtures for recommendations tests."""

import pytest

from client.recommendations import RecommendationsClient
from models.auth import TraktAuthToken


@pytest.fixture
def authenticated_client(mock_auth_token: TraktAuthToken) -> RecommendationsClient:
    """Create an authenticated recommendations client for testing."""
    client = RecommendationsClient()
    client.auth_token = mock_auth_token
    return client
