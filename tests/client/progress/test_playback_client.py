"""Tests for the PlaybackClient."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from client.progress.client import ProgressClient
    from models.progress.playback import PlaybackProgressResponse


class TestPlaybackClient:
    """Tests for PlaybackClient playback progress methods."""

    @pytest.mark.asyncio
    async def test_get_playback_progress_all(
        self,
        authenticated_progress_client: ProgressClient,
        sample_playback_progress_mixed: list[PlaybackProgressResponse],
    ) -> None:
        """Test retrieval of all playback progress items."""
        with patch.object(
            authenticated_progress_client, "_make_typed_list_request"
        ) as mock_request:
            mock_request.return_value = sample_playback_progress_mixed

            result = await authenticated_progress_client.get_playback_progress()

            assert len(result) == 2
            assert result[0]["type"] == "movie"
            assert result[1]["type"] == "episode"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_playback_progress_movies_only(
        self,
        authenticated_progress_client: ProgressClient,
        sample_playback_progress_movies: list[PlaybackProgressResponse],
    ) -> None:
        """Test retrieval of movies playback progress only."""
        with patch.object(
            authenticated_progress_client, "_make_typed_list_request"
        ) as mock_request:
            mock_request.return_value = sample_playback_progress_movies

            result = await authenticated_progress_client.get_playback_progress(
                playback_type="movies"
            )

            assert len(result) == 1
            assert result[0]["type"] == "movie"

            # Verify endpoint contains movies
            call_args = mock_request.call_args
            endpoint = (
                call_args.args[0]
                if call_args.args
                else call_args.kwargs.get("endpoint", "")
            )
            assert "movies" in endpoint

    @pytest.mark.asyncio
    async def test_get_playback_progress_episodes_only(
        self,
        authenticated_progress_client: ProgressClient,
        sample_playback_progress_episodes: list[PlaybackProgressResponse],
    ) -> None:
        """Test retrieval of episodes playback progress only."""
        with patch.object(
            authenticated_progress_client, "_make_typed_list_request"
        ) as mock_request:
            mock_request.return_value = sample_playback_progress_episodes

            result = await authenticated_progress_client.get_playback_progress(
                playback_type="episodes"
            )

            assert len(result) == 1
            assert result[0]["type"] == "episode"

            # Verify endpoint contains episodes
            call_args = mock_request.call_args
            endpoint = (
                call_args.args[0]
                if call_args.args
                else call_args.kwargs.get("endpoint", "")
            )
            assert "episodes" in endpoint

    @pytest.mark.asyncio
    async def test_get_playback_progress_not_authenticated(
        self,
        authenticated_progress_client: ProgressClient,
    ) -> None:
        """Test that unauthenticated requests raise ValueError."""
        # Remove authentication
        authenticated_progress_client.auth_token = None

        with pytest.raises(ValueError, match="authenticated"):
            await authenticated_progress_client.get_playback_progress()

    @pytest.mark.asyncio
    async def test_remove_playback_item_success(
        self,
        authenticated_progress_client: ProgressClient,
    ) -> None:
        """Test successful removal of a playback item."""
        with patch.object(
            authenticated_progress_client, "_delete_request"
        ) as mock_delete:
            mock_delete.return_value = None

            await authenticated_progress_client.remove_playback_item(12345)

            mock_delete.assert_called_once()
            call_args = mock_delete.call_args
            endpoint = (
                call_args.args[0]
                if call_args.args
                else call_args.kwargs.get("endpoint", "")
            )
            assert "12345" in endpoint

    @pytest.mark.asyncio
    async def test_remove_playback_item_not_authenticated(
        self,
        authenticated_progress_client: ProgressClient,
    ) -> None:
        """Test that unauthenticated removal raises ValueError."""
        # Remove authentication
        authenticated_progress_client.auth_token = None

        with pytest.raises(ValueError, match="authenticated"):
            await authenticated_progress_client.remove_playback_item(12345)
