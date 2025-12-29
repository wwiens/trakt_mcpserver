"""Tests for comment client pagination functionality."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.comments.details import CommentDetailsClient
from client.comments.episode import EpisodeCommentsClient
from client.comments.movie import MovieCommentsClient
from client.comments.season import SeasonCommentsClient
from client.comments.show import ShowCommentsClient
from models.types.pagination import PaginatedResponse


def _make_httpx_mock(*responses: MagicMock) -> MagicMock:
    """Create a mock httpx.AsyncClient with standard async methods.

    Args:
        *responses: Mock response objects to return. If multiple, uses side_effect.
                   If single, behaves like return_value for first call.

    Returns:
        Configured mock instance with get, post, and aclose methods.
    """
    mock_instance = MagicMock()
    if responses:
        mock_instance.get = AsyncMock(side_effect=list(responses))
    else:
        mock_instance.get = AsyncMock()
    mock_instance.post = AsyncMock()
    mock_instance.aclose = AsyncMock()
    return mock_instance


@pytest.mark.asyncio
async def test_movie_comments_no_page_respects_limit():
    """Test that movie comments with no page parameter respects limit as max items."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "comment": "Great movie!",
            "user": {"username": "user1"},
            "created_at": "2024-01-01T00:00:00Z",
        },
        {
            "id": 2,
            "comment": "Amazing!",
            "user": {"username": "user2"},
            "created_at": "2024-01-02T00:00:00Z",
        },
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "4",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = MovieCommentsClient()
        result = await client.get_movie_comments("test-movie", limit=2, page=None)

        # Should return exactly 2 comments (capped by limit)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2


@pytest.mark.asyncio
async def test_movie_comments_with_page_returns_paginated():
    """Test that movie comments with page parameter returns PaginatedResponse."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "comment": "Great movie!",
            "user": {"username": "user1"},
            "created_at": "2024-01-01T00:00:00Z",
        },
        {
            "id": 2,
            "comment": "Amazing!",
            "user": {"username": "user2"},
            "created_at": "2024-01-02T00:00:00Z",
        },
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "2",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "6",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = MovieCommentsClient()
        result = await client.get_movie_comments("test-movie", limit=2, page=1)

        # Should return PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert result.pagination.current_page == 1
        assert result.pagination.total_pages == 3
        assert result.pagination.total_items == 6
        assert result.pagination.has_next_page
        assert not result.pagination.has_previous_page


@pytest.mark.asyncio
async def test_show_comments_pagination():
    """Test that show comments supports pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "comment": "Great show!",
            "user": {"username": "user1"},
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "5",
        "X-Pagination-Item-Count": "50",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = ShowCommentsClient()
        result = await client.get_show_comments("test-show", limit=10, page=2)

        assert isinstance(result, PaginatedResponse)
        assert result.pagination.current_page == 2
        assert result.pagination.has_previous_page
        assert result.pagination.has_next_page


@pytest.mark.asyncio
async def test_season_comments_pagination():
    """Test that season comments supports pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "comment": "Great season!",
            "user": {"username": "user1"},
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "5",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = SeasonCommentsClient()
        result = await client.get_season_comments("test-show", 1, limit=10, page=1)

        assert isinstance(result, PaginatedResponse)
        assert result.pagination.current_page == 1
        assert result.pagination.total_pages == 1
        assert not result.pagination.has_next_page
        assert not result.pagination.has_previous_page


@pytest.mark.asyncio
async def test_episode_comments_pagination():
    """Test that episode comments supports pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "comment": "Great episode!",
            "user": {"username": "user1"},
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]
    mock_response.headers = {
        "X-Pagination-Page": "3",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "3",
        "X-Pagination-Item-Count": "30",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = EpisodeCommentsClient()
        result = await client.get_episode_comments("test-show", 1, 1, limit=10, page=3)

        assert isinstance(result, PaginatedResponse)
        assert result.pagination.current_page == 3
        assert result.pagination.total_pages == 3
        assert not result.pagination.has_next_page
        assert result.pagination.has_previous_page


@pytest.mark.asyncio
async def test_comment_replies_pagination():
    """Test that comment replies supports pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "comment": "I agree!",
            "user": {"username": "user1"},
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "2",
        "X-Pagination-Item-Count": "15",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = CommentDetailsClient()
        result = await client.get_comment_replies("test-comment", limit=10, page=1)

        assert isinstance(result, PaginatedResponse)
        assert result.pagination.current_page == 1
        assert result.pagination.total_pages == 2
        assert result.pagination.has_next_page


@pytest.mark.asyncio
async def test_comments_pagination_metadata():
    """Test that pagination metadata is correctly extracted."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "comment": "Test comment",
            "user": {"username": "user1"},
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]
    mock_response.headers = {
        "X-Pagination-Page": "2",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "5",
        "X-Pagination-Item-Count": "47",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = MovieCommentsClient()
        result = await client.get_movie_comments("test-movie", limit=10, page=2)

        assert isinstance(result, PaginatedResponse)
        assert result.pagination.current_page == 2
        assert result.pagination.items_per_page == 10
        assert result.pagination.total_pages == 5
        assert result.pagination.total_items == 47
        assert result.pagination.next_page() == 3
        assert result.pagination.previous_page() == 1


@pytest.mark.asyncio
async def test_comments_sort_with_pagination():
    """Test that sorting works with pagination."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "comment": "Oldest comment",
            "user": {"username": "user1"},
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "1",
        "X-Pagination-Item-Count": "1",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = MovieCommentsClient()
        result = await client.get_movie_comments(
            "test-movie", limit=10, page=1, sort="oldest"
        )

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert result.data[0]["comment"] == "Oldest comment"


@pytest.mark.asyncio
async def test_empty_comments_zero_pages():
    """Test handling of empty result set with total_pages=0."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.headers = {
        "X-Pagination-Page": "1",
        "X-Pagination-Limit": "10",
        "X-Pagination-Page-Count": "0",  # Zero pages for empty results
        "X-Pagination-Item-Count": "0",
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_instance = _make_httpx_mock(mock_response)
        mock_client.return_value = mock_instance

        client = ShowCommentsClient()
        result = await client.get_show_comments("show-with-no-comments", page=1)

        # Should successfully return empty PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 0
        assert result.pagination.total_pages == 0
        assert result.pagination.total_items == 0
        assert not result.pagination.has_next_page
        assert not result.pagination.has_previous_page
        assert result.pagination.next_page() is None
        assert result.is_empty
