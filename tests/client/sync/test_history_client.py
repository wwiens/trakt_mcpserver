"""Tests for the SyncHistoryClient."""

from __future__ import annotations

import time
from contextlib import suppress
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from models.sync.history import (
    HistoryEpisodeInfo,
    HistoryMovieInfo,
    HistoryNotFound,
    HistoryShowInfo,
    HistorySummary,
    HistorySummaryCount,
    TraktHistoryItem,
    TraktHistoryRequest,
    WatchHistoryItem,
)
from models.types.pagination import PaginatedResponse, PaginationMetadata

if TYPE_CHECKING:
    from collections.abc import Generator

    from client.sync.client import SyncClient
    from models.auth.auth import TraktAuthToken


# Sample API response data
SAMPLE_MOVIE_HISTORY_ITEM = {
    "id": 123456,
    "watched_at": "2024-01-15T20:30:00.000Z",
    "action": "watch",
    "type": "movie",
    "movie": {
        "title": "Inception",
        "year": 2010,
        "ids": {"trakt": 16662, "imdb": "tt1375666"},
    },
}

SAMPLE_EPISODE_HISTORY_ITEM = {
    "id": 123457,
    "watched_at": "2024-01-16T21:00:00.000Z",
    "action": "watch",
    "type": "episode",
    "episode": {
        "season": 1,
        "number": 1,
        "title": "Pilot",
        "ids": {"trakt": 62085},
    },
    "show": {
        "title": "Breaking Bad",
        "year": 2008,
        "ids": {"trakt": 1388},
    },
}


def create_movie_history_item() -> WatchHistoryItem:
    """Create a sample movie watch history item."""
    return WatchHistoryItem(
        id=123456,
        watched_at="2024-01-15T20:30:00.000Z",
        action="watch",
        type="movie",
        movie=HistoryMovieInfo(
            title="Inception",
            year=2010,
            ids={"trakt": 16662, "imdb": "tt1375666"},
        ),
    )


def create_episode_history_item() -> WatchHistoryItem:
    """Create a sample episode watch history item."""
    return WatchHistoryItem(
        id=123457,
        watched_at="2024-01-16T21:00:00.000Z",
        action="watch",
        type="episode",
        episode=HistoryEpisodeInfo(
            season=1,
            number=1,
            title="Pilot",
            ids={"trakt": 62085},
        ),
        show=HistoryShowInfo(
            title="Breaking Bad",
            year=2008,
            ids={"trakt": 1388},
        ),
    )


def create_history_summary(
    *, added_movies: int = 0, deleted_movies: int = 0
) -> HistorySummary:
    """Create a sample history summary."""
    return HistorySummary(
        added=HistorySummaryCount(movies=added_movies, shows=0, seasons=0, episodes=0)
        if added_movies
        else None,
        deleted=HistorySummaryCount(
            movies=deleted_movies, shows=0, seasons=0, episodes=0
        )
        if deleted_movies
        else None,
        not_found=HistoryNotFound(movies=[], shows=[], seasons=[], episodes=[]),
    )


def create_paginated_response(
    items: list[WatchHistoryItem],
) -> PaginatedResponse[WatchHistoryItem]:
    """Create a paginated response wrapper for testing."""
    return PaginatedResponse(
        data=items,
        pagination=PaginationMetadata(
            current_page=1,
            items_per_page=10,
            total_pages=1,
            total_items=len(items),
        ),
    )


@pytest.fixture
def mock_auth_token() -> TraktAuthToken:
    """Create a mock auth token for testing."""
    from models.auth import TraktAuthToken

    return TraktAuthToken(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )


@pytest.fixture
def authenticated_sync_client(
    mock_auth_token: TraktAuthToken,
) -> Generator[SyncClient, None, None]:
    """Create an authenticated sync client for testing."""
    from client.sync.client import SyncClient

    client = SyncClient()
    client.auth_token = mock_auth_token

    yield client

    if hasattr(client, "close"):
        with suppress(Exception):
            client.close()  # type: ignore[attr-defined]


class TestSyncHistoryClient:
    """Tests for SyncHistoryClient methods."""

    @pytest.mark.asyncio
    async def test_get_history_all(
        self,
        authenticated_sync_client: SyncClient,
    ) -> None:
        """Test retrieval of all watch history."""
        with patch.object(
            authenticated_sync_client, "_make_paginated_request"
        ) as mock_request:
            mock_items = [create_movie_history_item(), create_episode_history_item()]
            mock_request.return_value = create_paginated_response(mock_items)

            result = await authenticated_sync_client.get_history()

            assert len(result.data) == 2
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_history_movies_type(
        self,
        authenticated_sync_client: SyncClient,
    ) -> None:
        """Test retrieval of movies watch history."""
        with patch.object(
            authenticated_sync_client, "_make_paginated_request"
        ) as mock_request:
            mock_request.return_value = create_paginated_response(
                [create_movie_history_item()]
            )

            result = await authenticated_sync_client.get_history(history_type="movies")

            assert len(result.data) == 1
            assert result.data[0].type == "movie"

            # Verify endpoint contains movies
            call_args = mock_request.call_args
            endpoint = call_args.args[0] if call_args.args else ""
            assert "movies" in endpoint

    @pytest.mark.asyncio
    async def test_get_history_specific_item(
        self,
        authenticated_sync_client: SyncClient,
    ) -> None:
        """Test retrieval of watch history for a specific item."""
        with patch.object(
            authenticated_sync_client, "_make_paginated_request"
        ) as mock_request:
            mock_request.return_value = create_paginated_response(
                [create_movie_history_item()]
            )

            result = await authenticated_sync_client.get_history(
                history_type="movies",
                item_id="16662",
            )

            assert len(result.data) == 1
            assert result.data[0].movie.title == "Inception"

            # Verify endpoint contains item_id
            call_args = mock_request.call_args
            endpoint = call_args.args[0] if call_args.args else ""
            assert "16662" in endpoint

    @pytest.mark.asyncio
    async def test_get_history_date_range(
        self,
        authenticated_sync_client: SyncClient,
    ) -> None:
        """Test retrieval with date range filters."""
        with patch.object(
            authenticated_sync_client, "_make_paginated_request"
        ) as mock_request:
            mock_request.return_value = create_paginated_response(
                [create_movie_history_item()]
            )

            await authenticated_sync_client.get_history(
                start_at="2024-01-01T00:00:00.000Z",
                end_at="2024-12-31T23:59:59.000Z",
            )

            # Verify params include date filters
            call_kwargs = mock_request.call_args.kwargs
            params = call_kwargs.get("params", {})
            assert params.get("start_at") == "2024-01-01T00:00:00.000Z"
            assert params.get("end_at") == "2024-12-31T23:59:59.000Z"

    @pytest.mark.asyncio
    async def test_get_history_item_id_requires_type(
        self,
        authenticated_sync_client: SyncClient,
    ) -> None:
        """Test that item_id without history_type raises ValueError."""
        with pytest.raises(ValueError, match="history_type is required"):
            await authenticated_sync_client.get_history(item_id="16662")

    @pytest.mark.asyncio
    async def test_get_history_not_authenticated(
        self,
        authenticated_sync_client: SyncClient,
    ) -> None:
        """Test that unauthenticated requests raise ValueError."""
        authenticated_sync_client.auth_token = None

        with pytest.raises(ValueError, match="authenticated"):
            await authenticated_sync_client.get_history()

    @pytest.mark.asyncio
    async def test_add_to_history_success(
        self,
        authenticated_sync_client: SyncClient,
    ) -> None:
        """Test adding items to history."""
        with patch.object(
            authenticated_sync_client, "_post_typed_request"
        ) as mock_request:
            mock_request.return_value = create_history_summary(added_movies=1)

            request = TraktHistoryRequest(
                movies=[TraktHistoryItem(ids={"trakt": 16662})],
                shows=[],
                seasons=[],
                episodes=[],
            )

            result = await authenticated_sync_client.add_to_history(request)

            assert result.added.movies == 1
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_from_history_success(
        self,
        authenticated_sync_client: SyncClient,
    ) -> None:
        """Test removing items from history."""
        with patch.object(
            authenticated_sync_client, "_post_typed_request"
        ) as mock_request:
            mock_request.return_value = create_history_summary(deleted_movies=1)

            request = TraktHistoryRequest(
                movies=[TraktHistoryItem(ids={"trakt": 16662})],
                shows=[],
                seasons=[],
                episodes=[],
            )

            result = await authenticated_sync_client.remove_from_history(request)

            assert result.deleted.movies == 1
            mock_request.assert_called_once()
