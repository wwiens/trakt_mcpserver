"""Fixtures for progress client tests."""

from __future__ import annotations

import time
from contextlib import suppress
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from models.progress.playback import (
    PlaybackEpisodeInfo,
    PlaybackMovieInfo,
    PlaybackProgressResponse,
    PlaybackShowInfo,
)
from models.progress.show_progress import (
    EpisodeInfo,
    EpisodeProgressResponse,
    SeasonProgressResponse,
    ShowProgressResponse,
)
from models.types.ids import TraktIds

if TYPE_CHECKING:
    from collections.abc import Generator

    from client.progress.client import ProgressClient
    from models.auth.auth import TraktAuthToken


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
def authenticated_progress_client(
    mock_auth_token: TraktAuthToken,
) -> Generator[ProgressClient, None, None]:
    """Create an authenticated progress client for testing."""
    from client.progress.client import ProgressClient

    client = ProgressClient()
    client.auth_token = mock_auth_token

    yield client

    # Cleanup
    if hasattr(client, "close"):
        with suppress(Exception):
            client.close()  # type: ignore[attr-defined]


@pytest.fixture
def sample_show_progress_response() -> ShowProgressResponse:
    """Sample show progress response data for testing."""
    return ShowProgressResponse(
        aired=62,
        completed=45,
        last_watched_at="2024-01-15T20:30:00.000Z",
        reset_at=None,
        seasons=[
            SeasonProgressResponse(
                number=1,
                title="Season 1",
                aired=7,
                completed=7,
                episodes=[
                    EpisodeProgressResponse(
                        number=1,
                        completed=True,
                        last_watched_at="2024-01-01T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=2,
                        completed=True,
                        last_watched_at="2024-01-02T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=3,
                        completed=True,
                        last_watched_at="2024-01-03T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=4,
                        completed=True,
                        last_watched_at="2024-01-04T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=5,
                        completed=True,
                        last_watched_at="2024-01-05T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=6,
                        completed=True,
                        last_watched_at="2024-01-06T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=7,
                        completed=True,
                        last_watched_at="2024-01-07T10:00:00.000Z",
                    ),
                ],
            ),
            SeasonProgressResponse(
                number=2,
                title="Season 2",
                aired=13,
                completed=10,
                episodes=[
                    EpisodeProgressResponse(
                        number=1,
                        completed=True,
                        last_watched_at="2024-01-08T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=2,
                        completed=True,
                        last_watched_at="2024-01-09T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=3,
                        completed=True,
                        last_watched_at="2024-01-10T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=4,
                        completed=True,
                        last_watched_at="2024-01-11T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=5,
                        completed=True,
                        last_watched_at="2024-01-12T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=6,
                        completed=True,
                        last_watched_at="2024-01-13T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=7,
                        completed=True,
                        last_watched_at="2024-01-14T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=8,
                        completed=True,
                        last_watched_at="2024-01-15T10:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=9,
                        completed=True,
                        last_watched_at="2024-01-15T15:00:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=10,
                        completed=True,
                        last_watched_at="2024-01-15T20:30:00.000Z",
                    ),
                    EpisodeProgressResponse(
                        number=11, completed=False, last_watched_at=None
                    ),
                    EpisodeProgressResponse(
                        number=12, completed=False, last_watched_at=None
                    ),
                    EpisodeProgressResponse(
                        number=13, completed=False, last_watched_at=None
                    ),
                ],
            ),
        ],
        hidden_seasons=[],
        next_episode=EpisodeInfo(
            season=2,
            number=11,
            title="Mandala",
            ids=TraktIds(trakt=62095, tvdb=349232, imdb="tt1232248", tmdb=62158),
        ),
        last_episode=EpisodeInfo(
            season=2,
            number=10,
            title="Over",
            ids=TraktIds(trakt=62094, tvdb=349231, imdb="tt1232247", tmdb=62157),
        ),
    )


@pytest.fixture
def sample_playback_progress_movies() -> list[PlaybackProgressResponse]:
    """Sample playback progress response for movies."""
    return [
        PlaybackProgressResponse(
            progress=45.5,
            paused_at=datetime(2024, 1, 20, 15, 30, 0, tzinfo=UTC),
            id=12345,
            type="movie",
            movie=PlaybackMovieInfo(
                title="Inception",
                year=2010,
                ids=TraktIds(
                    trakt=16662,
                    slug="inception-2010",
                    imdb="tt1375666",
                    tmdb=27205,
                ),
            ),
        )
    ]


@pytest.fixture
def sample_playback_progress_episodes() -> list[PlaybackProgressResponse]:
    """Sample playback progress response for episodes."""
    return [
        PlaybackProgressResponse(
            progress=23.7,
            paused_at=datetime(2024, 1, 21, 20, 0, 0, tzinfo=UTC),
            id=67890,
            type="episode",
            episode=PlaybackEpisodeInfo(
                season=1,
                number=5,
                title="Gray Matter",
                ids=TraktIds(
                    trakt=62089,
                    tvdb=349226,
                    imdb="tt1054725",
                    tmdb=62152,
                ),
            ),
            show=PlaybackShowInfo(
                title="Breaking Bad",
                year=2008,
                ids=TraktIds(
                    trakt=1388,
                    slug="breaking-bad",
                    tvdb=81189,
                    imdb="tt0903747",
                    tmdb=1396,
                ),
            ),
        )
    ]


@pytest.fixture
def sample_playback_progress_mixed(
    sample_playback_progress_movies: list[PlaybackProgressResponse],
    sample_playback_progress_episodes: list[PlaybackProgressResponse],
) -> list[PlaybackProgressResponse]:
    """Sample playback progress response with both movies and episodes."""
    return sample_playback_progress_movies + sample_playback_progress_episodes
