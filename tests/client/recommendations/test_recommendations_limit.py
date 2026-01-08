"""Tests for recommendations client - limit and filtering functionality.

Note: The Trakt recommendations API does not support pagination.
Use the limit parameter (max 100) to control number of results.
"""

import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from client.recommendations import RecommendationsClient
from models.auth import TraktAuthToken

if TYPE_CHECKING:
    from models.recommendations.recommendation import (
        TraktRecommendedMovie,
        TraktRecommendedShow,
    )


@pytest.fixture
def mock_auth_token() -> TraktAuthToken:
    """Create a mock auth token for testing."""
    return TraktAuthToken(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )


@pytest.fixture
def authenticated_client(mock_auth_token: TraktAuthToken) -> RecommendationsClient:
    """Create an authenticated recommendations client for testing."""
    client = RecommendationsClient()
    client.auth_token = mock_auth_token
    return client


@pytest.mark.asyncio
async def test_movie_recommendations_respects_limit(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that movie recommendations respects limit parameter."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Movie 1", "year": 2024, "ids": {"trakt": 1}},
        {"title": "Movie 2", "year": 2024, "ids": {"trakt": 2}},
    ]
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result: list[
        TraktRecommendedMovie
    ] = await authenticated_client.get_movie_recommendations(limit=2)

    # Should return a list
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].title == "Movie 1"
    assert result[1].title == "Movie 2"

    # Verify limit was passed
    call_args = patched_httpx_client.get.call_args
    params = call_args[1].get("params", {})
    assert params.get("limit") == 2


@pytest.mark.asyncio
async def test_show_recommendations_respects_limit(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that show recommendations respects limit parameter."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "Show 1", "year": 2024, "ids": {"trakt": 1}},
        {"title": "Show 2", "year": 2024, "ids": {"trakt": 2}},
    ]
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result: list[
        TraktRecommendedShow
    ] = await authenticated_client.get_show_recommendations(limit=2)

    # Should return a list
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].title == "Show 1"
    assert result[1].title == "Show 2"

    # Verify limit was passed
    call_args = patched_httpx_client.get.call_args
    params = call_args[1].get("params", {})
    assert params.get("limit") == 2


@pytest.mark.asyncio
async def test_empty_recommendations_result(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test handling of empty recommendations."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result: list[
        TraktRecommendedMovie
    ] = await authenticated_client.get_movie_recommendations(limit=10)

    # Should return empty list
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_recommendations_with_favorited_by(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test recommendations include favorited_by data."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "Popular Movie",
            "year": 2024,
            "ids": {"trakt": 1},
            "favorited_by": [
                {
                    "user": {
                        "username": "user1",
                        "private": False,
                        "name": "User One",
                        "vip": True,
                        "ids": {"slug": "user1"},
                    },
                    "notes": "Great movie!",
                },
            ],
        },
    ]
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result: list[
        TraktRecommendedMovie
    ] = await authenticated_client.get_movie_recommendations(limit=10)

    assert isinstance(result, list)
    assert len(result) == 1
    movie: TraktRecommendedMovie = result[0]
    assert movie.title == "Popular Movie"
    assert len(movie.favorited_by) == 1
    assert movie.favorited_by[0].user.username == "user1"
    assert movie.favorited_by[0].notes == "Great movie!"


@pytest.mark.asyncio
async def test_movie_recommendations_default_limit(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that movie recommendations uses default limit."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    await authenticated_client.get_movie_recommendations()

    # Verify default limit was passed (10)
    call_args = patched_httpx_client.get.call_args
    params = call_args[1].get("params", {})
    assert params.get("limit") == 10


@pytest.mark.asyncio
async def test_show_recommendations_default_limit(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test that show recommendations uses default limit."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    await authenticated_client.get_show_recommendations()

    # Verify default limit was passed (10)
    call_args = patched_httpx_client.get.call_args
    params = call_args[1].get("params", {})
    assert params.get("limit") == 10
