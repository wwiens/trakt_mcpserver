"""Tests for the progress tools."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from models.progress.playback import (
    PlaybackEpisodeInfo,
    PlaybackMovieInfo,
    PlaybackProgressResponse,
    PlaybackShowInfo,
)
from models.progress.show_progress import (
    EpisodeInfo,
    SeasonProgressResponse,
    ShowProgressResponse,
)
from models.types.ids import TraktIds
from server.progress.tools import (
    fetch_playback_progress,
    fetch_show_progress,
    register_progress_tools,
    remove_playback_item,
)


class TestFetchShowProgress:
    """Tests for fetch_show_progress tool."""

    @pytest.mark.asyncio
    async def test_fetch_show_progress_success(self) -> None:
        """Test successful fetch of show progress."""
        mock_progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=62,
            completed=45,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[
                SeasonProgressResponse(number=1, aired=7, completed=7, episodes=[]),
                SeasonProgressResponse(number=2, aired=13, completed=10, episodes=[]),
            ],
            next_episode=EpisodeInfo(
                season=2,
                number=11,
                title="Mandala",
                ids=TraktIds(trakt=62095),
            ),
        )

        with patch("server.progress.tools.ProgressClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_show_progress = AsyncMock(return_value=mock_progress)

            result = await fetch_show_progress("breaking-bad")

            assert "# Show Progress: breaking-bad" in result
            assert "45/62 episodes" in result
            assert "72.6%" in result
            mock_client.get_show_progress.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_show_progress_with_next_episode(self) -> None:
        """Test show progress with next episode information."""
        mock_progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=10,
            completed=5,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[],
            next_episode=EpisodeInfo(
                season=1,
                number=6,
                title="Next Episode Title",
                ids=TraktIds(trakt=12345),
            ),
        )

        with patch("server.progress.tools.ProgressClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_show_progress = AsyncMock(return_value=mock_progress)

            result = await fetch_show_progress("test-show")

            assert "## Up Next" in result
            assert "S01E06" in result
            assert "Next Episode Title" in result

    @pytest.mark.asyncio
    async def test_fetch_show_progress_completed_show(self) -> None:
        """Test show progress for a fully completed show."""
        mock_progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=62,
            completed=62,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[
                SeasonProgressResponse(number=1, aired=7, completed=7, episodes=[]),
            ],
        )

        with patch("server.progress.tools.ProgressClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_show_progress = AsyncMock(return_value=mock_progress)

            result = await fetch_show_progress("test-show")

            assert "62/62 episodes" in result
            assert "100.0%" in result


class TestFetchPlaybackProgress:
    """Tests for fetch_playback_progress tool."""

    @pytest.mark.asyncio
    async def test_fetch_playback_progress_empty(self) -> None:
        """Test playback progress with no paused items."""
        with patch("server.progress.tools.ProgressClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_playback_progress = AsyncMock(return_value=[])

            result = await fetch_playback_progress()

            assert "No paused playback items found" in result

    @pytest.mark.asyncio
    async def test_fetch_playback_progress_with_movies(self) -> None:
        """Test playback progress with movie items."""
        mock_playback = [
            PlaybackProgressResponse(
                progress=45.5,
                paused_at=datetime(2024, 1, 20, 15, 30, 0, tzinfo=UTC),
                id=12345,
                type="movie",
                movie=PlaybackMovieInfo(
                    title="Inception",
                    year=2010,
                    ids=TraktIds(trakt=16662),
                ),
            )
        ]

        with patch("server.progress.tools.ProgressClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_playback_progress = AsyncMock(return_value=mock_playback)

            result = await fetch_playback_progress()

            assert "## Movies" in result
            assert "Inception (2010)" in result
            assert "45.5%" in result
            assert "ID: 12345" in result

    @pytest.mark.asyncio
    async def test_fetch_playback_progress_with_episodes(self) -> None:
        """Test playback progress with episode items."""
        mock_playback = [
            PlaybackProgressResponse(
                progress=23.7,
                paused_at=datetime(2024, 1, 21, 20, 0, 0, tzinfo=UTC),
                id=67890,
                type="episode",
                episode=PlaybackEpisodeInfo(
                    season=1,
                    number=5,
                    title="Gray Matter",
                    ids=TraktIds(trakt=62089),
                ),
                show=PlaybackShowInfo(
                    title="Breaking Bad",
                    year=2008,
                    ids=TraktIds(trakt=1388),
                ),
            )
        ]

        with patch("server.progress.tools.ProgressClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get_playback_progress = AsyncMock(return_value=mock_playback)

            result = await fetch_playback_progress()

            assert "## Episodes" in result
            assert "Breaking Bad - S01E05" in result
            assert "Gray Matter" in result
            assert "23.7%" in result


class TestRemovePlaybackItem:
    """Tests for remove_playback_item tool."""

    @pytest.mark.asyncio
    async def test_remove_playback_item_success(self) -> None:
        """Test successful removal of playback item."""
        with patch("server.progress.tools.ProgressClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.remove_playback_item = AsyncMock(return_value=None)

            result = await remove_playback_item(12345)

            assert "Successfully removed" in result
            assert "12345" in result
            mock_client.remove_playback_item.assert_called_once_with(12345)


class TestRegisterProgressTools:
    """Tests for register_progress_tools function."""

    def test_register_progress_tools(self) -> None:
        """Test that progress tools are registered correctly."""
        from unittest.mock import MagicMock

        mock_mcp = MagicMock()

        handlers = register_progress_tools(mock_mcp)

        assert len(handlers) == 3
        assert mock_mcp.tool.call_count == 3
