"""Tests for recommendations client."""

from collections.abc import Generator
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.recommendations import RecommendationsClient
from utils.api.error_types import AuthenticationRequiredError

if TYPE_CHECKING:
    from models.recommendations.recommendation import (
        TraktRecommendedMovie,
        TraktRecommendedShow,
    )


@pytest.fixture
def patched_httpx_with_delete(
    mock_httpx_client: MagicMock,
) -> Generator[MagicMock, None, None]:
    """Patch httpx.AsyncClient with delete support."""
    mock_httpx_client.delete = AsyncMock()
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value = mock_httpx_client
        yield mock_httpx_client


@pytest.mark.asyncio
async def test_get_movie_recommendations_not_authenticated(
    trakt_env: None,
) -> None:
    """Test that get_movie_recommendations requires authentication."""
    client = RecommendationsClient()
    # Mock is_authenticated to return False (in case auth_token.json exists)
    client.is_authenticated = MagicMock(return_value=False)
    with pytest.raises(AuthenticationRequiredError):
        await client.get_movie_recommendations()


@pytest.mark.asyncio
async def test_get_show_recommendations_not_authenticated(
    trakt_env: None,
) -> None:
    """Test that get_show_recommendations requires authentication."""
    client = RecommendationsClient()
    # Mock is_authenticated to return False (in case auth_token.json exists)
    client.is_authenticated = MagicMock(return_value=False)
    with pytest.raises(AuthenticationRequiredError):
        await client.get_show_recommendations()


@pytest.mark.asyncio
async def test_hide_movie_recommendation_not_authenticated(
    trakt_env: None,
) -> None:
    """Test that hide_movie_recommendation requires authentication."""
    client = RecommendationsClient()
    # Mock is_authenticated to return False (in case auth_token.json exists)
    client.is_authenticated = MagicMock(return_value=False)
    with pytest.raises(AuthenticationRequiredError):
        await client.hide_movie_recommendation("tron-legacy-2010")


@pytest.mark.asyncio
async def test_hide_show_recommendation_not_authenticated(
    trakt_env: None,
) -> None:
    """Test that hide_show_recommendation requires authentication."""
    client = RecommendationsClient()
    # Mock is_authenticated to return False (in case auth_token.json exists)
    client.is_authenticated = MagicMock(return_value=False)
    with pytest.raises(AuthenticationRequiredError):
        await client.hide_show_recommendation("breaking-bad")


@pytest.mark.asyncio
async def test_unhide_movie_recommendation_not_authenticated(
    trakt_env: None,
) -> None:
    """Test that unhide_movie_recommendation requires authentication."""
    client = RecommendationsClient()
    # Mock is_authenticated to return False (in case auth_token.json exists)
    client.is_authenticated = MagicMock(return_value=False)
    with pytest.raises(AuthenticationRequiredError):
        await client.unhide_movie_recommendation("tron-legacy-2010")


@pytest.mark.asyncio
async def test_unhide_show_recommendation_not_authenticated(
    trakt_env: None,
) -> None:
    """Test that unhide_show_recommendation requires authentication."""
    client = RecommendationsClient()
    # Mock is_authenticated to return False (in case auth_token.json exists)
    client.is_authenticated = MagicMock(return_value=False)
    with pytest.raises(AuthenticationRequiredError):
        await client.unhide_show_recommendation("breaking-bad")


@pytest.mark.asyncio
async def test_get_movie_recommendations_success(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test successful movie recommendations fetch."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "TRON: Legacy",
            "year": 2010,
            "ids": {"trakt": 1, "slug": "tron-legacy-2010", "imdb": "tt1104001"},
        },
        {
            "title": "The Matrix",
            "year": 1999,
            "ids": {"trakt": 2, "slug": "the-matrix-1999", "imdb": "tt0133093"},
        },
    ]
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result: list[
        TraktRecommendedMovie
    ] = await authenticated_client.get_movie_recommendations(limit=10)

    # Should return a list (no pagination support)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].title == "TRON: Legacy"
    assert result[0].year == 2010
    assert result[1].title == "The Matrix"


@pytest.mark.asyncio
async def test_get_show_recommendations_success(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test successful show recommendations fetch."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": 1388, "slug": "breaking-bad", "imdb": "tt0903747"},
        },
        {
            "title": "Game of Thrones",
            "year": 2011,
            "ids": {"trakt": 1390, "slug": "game-of-thrones", "imdb": "tt0944947"},
        },
    ]
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result: list[
        TraktRecommendedShow
    ] = await authenticated_client.get_show_recommendations(limit=10)

    # Should return a list (no pagination support)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].title == "Breaking Bad"
    assert result[0].year == 2008
    assert result[1].title == "Game of Thrones"


@pytest.mark.asyncio
async def test_hide_movie_recommendation_success(
    trakt_env: None,
    patched_httpx_with_delete: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test successful hiding of a movie recommendation."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    patched_httpx_with_delete.delete.return_value = mock_response

    result = await authenticated_client.hide_movie_recommendation("tron-legacy-2010")

    assert result is True
    patched_httpx_with_delete.delete.assert_called_once()
    call_args = patched_httpx_with_delete.delete.call_args
    assert "/recommendations/movies/tron-legacy-2010" in call_args[0][0]


@pytest.mark.asyncio
async def test_hide_show_recommendation_success(
    trakt_env: None,
    patched_httpx_with_delete: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test successful hiding of a show recommendation."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    patched_httpx_with_delete.delete.return_value = mock_response

    result = await authenticated_client.hide_show_recommendation("breaking-bad")

    assert result is True
    patched_httpx_with_delete.delete.assert_called_once()
    call_args = patched_httpx_with_delete.delete.call_args
    assert "/recommendations/shows/breaking-bad" in call_args[0][0]


@pytest.mark.asyncio
async def test_unhide_movie_recommendation_success(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test successful unhiding of a movie recommendation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"deleted": {"movies": 1}}
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.post.return_value = mock_response

    result = await authenticated_client.unhide_movie_recommendation("tron-legacy-2010")

    assert result is True
    patched_httpx_client.post.assert_called_once()
    call_args = patched_httpx_client.post.call_args
    assert "/users/hidden/recommendations/remove" in call_args[0][0]


@pytest.mark.asyncio
async def test_unhide_show_recommendation_success(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test successful unhiding of a show recommendation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"deleted": {"shows": 1}}
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.post.return_value = mock_response

    result = await authenticated_client.unhide_show_recommendation("breaking-bad")

    assert result is True
    patched_httpx_client.post.assert_called_once()
    call_args = patched_httpx_client.post.call_args
    assert "/users/hidden/recommendations/remove" in call_args[0][0]


@pytest.mark.asyncio
async def test_get_movie_recommendations_with_filters(
    trakt_env: None,
    patched_httpx_client: MagicMock,
    authenticated_client: RecommendationsClient,
) -> None:
    """Test movie recommendations with ignore_collected and ignore_watchlisted."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "New Movie",
            "year": 2024,
            "ids": {"trakt": 999, "slug": "new-movie-2024"},
        },
    ]
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    result: list[
        TraktRecommendedMovie
    ] = await authenticated_client.get_movie_recommendations(
        limit=10, ignore_collected=True, ignore_watchlisted=True
    )

    assert isinstance(result, list)
    assert len(result) == 1

    # Verify the filters were passed
    call_args = patched_httpx_client.get.call_args
    params = call_args[1].get("params", {})
    assert params.get("ignore_collected") == "true"
    assert params.get("ignore_watchlisted") == "true"
