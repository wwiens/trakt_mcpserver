"""Tests for progress formatters."""

from __future__ import annotations

from typing import TYPE_CHECKING

from models.formatters.progress import ProgressFormatters

if TYPE_CHECKING:
    from models.progress.playback import PlaybackProgressResponse
    from models.progress.show_progress import ShowProgressResponse


class TestProgressFormatters:
    """Tests for ProgressFormatters class."""

    def test_format_show_progress_basic(self) -> None:
        """Test basic show progress formatting."""
        progress: ShowProgressResponse = {
            "aired": 10,
            "completed": 5,
            "last_watched_at": "2024-01-15T20:30:00.000Z",
            "seasons": [],
        }

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "# Show Progress: test-show" in result
        assert "5/10 episodes" in result
        assert "50.0%" in result
        assert "Last Watched:" in result

    def test_format_show_progress_with_seasons(self) -> None:
        """Test show progress with season breakdown."""
        progress: ShowProgressResponse = {
            "aired": 20,
            "completed": 17,
            "last_watched_at": "2024-01-15T20:30:00.000Z",
            "seasons": [
                {"number": 1, "aired": 10, "completed": 10, "episodes": []},
                {"number": 2, "aired": 10, "completed": 7, "episodes": []},
            ],
        }

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "## Season Progress" in result
        assert "Season 1:" in result
        assert "Complete (100%)" in result
        assert "Season 2:" in result
        assert "7/10" in result

    def test_format_show_progress_with_specials(self) -> None:
        """Test show progress with specials season."""
        progress: ShowProgressResponse = {
            "aired": 12,
            "completed": 10,
            "last_watched_at": "2024-01-15T20:30:00.000Z",
            "seasons": [
                {"number": 0, "aired": 2, "completed": 2, "episodes": []},
                {"number": 1, "aired": 10, "completed": 8, "episodes": []},
            ],
        }

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "Specials:" in result
        assert "Season 1:" in result

    def test_format_show_progress_completed(self) -> None:
        """Test show progress for 100% completed show."""
        progress: ShowProgressResponse = {
            "aired": 62,
            "completed": 62,
            "last_watched_at": "2024-01-15T20:30:00.000Z",
            "seasons": [
                {"number": 1, "aired": 7, "completed": 7, "episodes": []},
                {"number": 2, "aired": 13, "completed": 13, "episodes": []},
            ],
        }

        result = ProgressFormatters.format_show_progress(progress, "breaking-bad")

        assert "62/62 episodes" in result
        assert "100.0%" in result

    def test_format_show_progress_with_next_episode(self) -> None:
        """Test show progress with next episode info."""
        progress: ShowProgressResponse = {
            "aired": 10,
            "completed": 5,
            "last_watched_at": "2024-01-15T20:30:00.000Z",
            "seasons": [],
            "next_episode": {
                "season": 1,
                "number": 6,
                "title": "Next Episode",
                "ids": {"trakt": 12345},
            },
        }

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "## Up Next" in result
        assert "S01E06" in result
        assert "Next Episode" in result

    def test_format_show_progress_with_last_episode(self) -> None:
        """Test show progress with last watched episode info."""
        progress: ShowProgressResponse = {
            "aired": 10,
            "completed": 5,
            "last_watched_at": "2024-01-15T20:30:00.000Z",
            "seasons": [],
            "last_episode": {
                "season": 1,
                "number": 5,
                "title": "Last Watched",
                "ids": {"trakt": 12344},
            },
        }

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "## Last Watched" in result
        assert "S01E05" in result
        assert "Last Watched" in result

    def test_format_show_progress_with_hidden_seasons(self) -> None:
        """Test show progress with hidden seasons."""
        progress: ShowProgressResponse = {
            "aired": 10,
            "completed": 5,
            "last_watched_at": "2024-01-15T20:30:00.000Z",
            "seasons": [],
            "hidden_seasons": [
                {"number": 3, "ids": {"trakt": 12345}},
            ],
        }

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "## Hidden Seasons" in result
        assert "Season 3" in result

    def test_format_playback_progress_empty(self) -> None:
        """Test playback progress with no items."""
        result = ProgressFormatters.format_playback_progress([])

        assert "No paused playback items found" in result
        assert "Items appear here when you pause" in result

    def test_format_playback_progress_movies(self) -> None:
        """Test playback progress with movie items."""
        items: list[PlaybackProgressResponse] = [
            {
                "progress": 45.5,
                "paused_at": "2024-01-20T15:30:00.000Z",
                "id": 12345,
                "type": "movie",
                "movie": {
                    "title": "Inception",
                    "year": 2010,
                    "ids": {"trakt": 16662},
                },
            }
        ]

        result = ProgressFormatters.format_playback_progress(items)

        assert "# Playback Progress (1 item)" in result
        assert "## Movies" in result
        assert "Inception (2010)" in result
        assert "Progress: 45.5%" in result
        assert "ID: 12345" in result

    def test_format_playback_progress_episodes(self) -> None:
        """Test playback progress with episode items."""
        items: list[PlaybackProgressResponse] = [
            {
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
        ]

        result = ProgressFormatters.format_playback_progress(items)

        assert "## Episodes" in result
        assert "Breaking Bad - S01E05" in result
        assert "Gray Matter" in result
        assert "Progress: 23.7%" in result

    def test_format_playback_progress_multiple_items(self) -> None:
        """Test playback progress with multiple items."""
        items: list[PlaybackProgressResponse] = [
            {
                "progress": 45.5,
                "paused_at": "2024-01-20T15:30:00.000Z",
                "id": 12345,
                "type": "movie",
                "movie": {"title": "Inception", "year": 2010, "ids": {"trakt": 16662}},
            },
            {
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
                "show": {"title": "Breaking Bad", "year": 2008, "ids": {"trakt": 1388}},
            },
        ]

        result = ProgressFormatters.format_playback_progress(items)

        assert "# Playback Progress (2 items)" in result
        assert "## Movies" in result
        assert "## Episodes" in result
