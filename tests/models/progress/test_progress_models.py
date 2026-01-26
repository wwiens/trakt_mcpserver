"""Tests for progress models."""

from typing import get_type_hints

from models.progress.playback import (
    PlaybackEpisodeInfo,
    PlaybackMovieInfo,
    PlaybackProgressResponse,
    PlaybackShowInfo,
)
from models.progress.show_progress import (
    EpisodeInfo,
    EpisodeProgressResponse,
    HiddenSeasonResponse,
    SeasonProgressResponse,
    ShowProgressResponse,
)


class TestShowProgressModels:
    """Tests for show progress TypedDict models."""

    def test_show_progress_response_structure(self) -> None:
        """Test ShowProgressResponse has expected fields."""
        hints = get_type_hints(ShowProgressResponse)

        # Required fields
        assert "aired" in hints
        assert "completed" in hints
        assert "last_watched_at" in hints
        assert "seasons" in hints

        # Optional fields (NotRequired)
        assert "reset_at" in hints
        assert "hidden_seasons" in hints
        assert "next_episode" in hints
        assert "last_episode" in hints

    def test_season_progress_response_structure(self) -> None:
        """Test SeasonProgressResponse has expected fields."""
        hints = get_type_hints(SeasonProgressResponse)

        assert "number" in hints
        assert "aired" in hints
        assert "completed" in hints
        assert "episodes" in hints

    def test_episode_progress_response_structure(self) -> None:
        """Test EpisodeProgressResponse has expected fields."""
        hints = get_type_hints(EpisodeProgressResponse)

        assert "number" in hints
        assert "completed" in hints
        assert "last_watched_at" in hints

    def test_episode_info_structure(self) -> None:
        """Test EpisodeInfo has expected fields."""
        hints = get_type_hints(EpisodeInfo)

        assert "season" in hints
        assert "number" in hints
        assert "title" in hints
        assert "ids" in hints

    def test_hidden_season_response_structure(self) -> None:
        """Test HiddenSeasonResponse has expected fields."""
        hints = get_type_hints(HiddenSeasonResponse)

        assert "number" in hints
        assert "ids" in hints


class TestPlaybackProgressModels:
    """Tests for playback progress TypedDict models."""

    def test_playback_progress_response_movie(self) -> None:
        """Test PlaybackProgressResponse with movie type."""
        movie_item: PlaybackProgressResponse = {
            "progress": 45.5,
            "paused_at": "2024-01-20T15:30:00.000Z",
            "id": 12345,
            "type": "movie",
            "movie": {
                "title": "Inception",
                "year": 2010,
                "ids": {"trakt": 16662, "imdb": "tt1375666"},
            },
        }

        assert movie_item["type"] == "movie"
        assert movie_item["progress"] == 45.5
        assert movie_item["movie"]["title"] == "Inception"

    def test_playback_progress_response_episode(self) -> None:
        """Test PlaybackProgressResponse with episode type."""
        episode_item: PlaybackProgressResponse = {
            "progress": 23.7,
            "paused_at": "2024-01-21T20:00:00.000Z",
            "id": 67890,
            "type": "episode",
            "episode": {
                "season": 1,
                "number": 5,
                "title": "Gray Matter",
                "ids": {"trakt": 62089},
            },
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": 1388},
            },
        }

        assert episode_item["type"] == "episode"
        assert episode_item["progress"] == 23.7
        assert episode_item["episode"]["season"] == 1
        assert episode_item["show"]["title"] == "Breaking Bad"

    def test_playback_movie_info_structure(self) -> None:
        """Test PlaybackMovieInfo has expected fields."""
        hints = get_type_hints(PlaybackMovieInfo)

        assert "title" in hints
        assert "year" in hints
        assert "ids" in hints

    def test_playback_episode_info_structure(self) -> None:
        """Test PlaybackEpisodeInfo has expected fields."""
        hints = get_type_hints(PlaybackEpisodeInfo)

        assert "season" in hints
        assert "number" in hints
        assert "title" in hints
        assert "ids" in hints

    def test_playback_show_info_structure(self) -> None:
        """Test PlaybackShowInfo has expected fields."""
        hints = get_type_hints(PlaybackShowInfo)

        assert "title" in hints
        assert "year" in hints
        assert "ids" in hints
