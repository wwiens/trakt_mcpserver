"""Tests for progress formatters."""

from __future__ import annotations

from models.formatters.progress import ProgressFormatters
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


class TestProgressFormatters:
    """Tests for ProgressFormatters class."""

    def test_format_show_progress_basic(self) -> None:
        """Test basic show progress formatting."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=10,
            completed=5,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[],
        )

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "# Show Progress: test-show" in result
        assert "5/10 episodes" in result
        assert "50.0%" in result
        assert "Last Watched:" in result

    def test_format_show_progress_with_seasons(self) -> None:
        """Test show progress with season breakdown."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=20,
            completed=17,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[
                SeasonProgressResponse(number=1, aired=10, completed=10, episodes=[]),
                SeasonProgressResponse(number=2, aired=10, completed=7, episodes=[]),
            ],
        )

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "## Season Progress" in result
        assert "Season 1:" in result
        assert "Complete (100%)" in result
        assert "Season 2:" in result
        assert "7/10" in result

    def test_format_show_progress_with_specials(self) -> None:
        """Test show progress with specials season."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=12,
            completed=10,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[
                SeasonProgressResponse(number=0, aired=2, completed=2, episodes=[]),
                SeasonProgressResponse(number=1, aired=10, completed=8, episodes=[]),
            ],
        )

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "Specials:" in result
        assert "Season 1:" in result

    def test_format_show_progress_completed(self) -> None:
        """Test show progress for 100% completed show."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=62,
            completed=62,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[
                SeasonProgressResponse(number=1, aired=7, completed=7, episodes=[]),
                SeasonProgressResponse(number=2, aired=13, completed=13, episodes=[]),
            ],
        )

        result = ProgressFormatters.format_show_progress(progress, "breaking-bad")

        assert "62/62 episodes" in result
        assert "100.0%" in result

    def test_format_show_progress_with_next_episode(self) -> None:
        """Test show progress with next episode info."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=10,
            completed=5,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[],
            next_episode=EpisodeInfo(
                season=1,
                number=6,
                title="Next Episode",
                ids={"trakt": 12345},
            ),
        )

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "## Up Next" in result
        assert "S01E06" in result
        assert "Next Episode" in result

    def test_format_show_progress_with_last_episode(self) -> None:
        """Test show progress with last watched episode info."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=10,
            completed=5,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[],
            last_episode=EpisodeInfo(
                season=1,
                number=5,
                title="Last Watched",
                ids={"trakt": 12344},
            ),
        )

        result = ProgressFormatters.format_show_progress(progress, "test-show")

        assert "## Last Watched" in result
        assert "S01E05" in result
        assert "Last Watched" in result

    def test_format_show_progress_with_hidden_seasons(self) -> None:
        """Test show progress with hidden seasons."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=10,
            completed=5,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[],
            hidden_seasons=[
                HiddenSeasonResponse(number=3, ids={"trakt": 12345}),
            ],
        )

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
        items = [
            PlaybackProgressResponse(
                progress=45.5,
                paused_at="2024-01-20T15:30:00.000Z",
                id=12345,
                type="movie",
                movie=PlaybackMovieInfo(
                    title="Inception",
                    year=2010,
                    ids={"trakt": 16662},
                ),
            )
        ]

        result = ProgressFormatters.format_playback_progress(items)

        assert "# Playback Progress (1 item)" in result
        assert "## Movies" in result
        assert "Inception (2010)" in result
        assert "Progress: 45.5%" in result
        assert "ID: 12345" in result

    def test_format_playback_progress_episodes(self) -> None:
        """Test playback progress with episode items."""
        items = [
            PlaybackProgressResponse(
                progress=23.7,
                paused_at="2024-01-21T20:00:00.000Z",
                id=67890,
                type="episode",
                episode=PlaybackEpisodeInfo(
                    season=1,
                    number=5,
                    title="Gray Matter",
                    ids={"trakt": 62089},
                ),
                show=PlaybackShowInfo(
                    title="Breaking Bad",
                    year=2008,
                    ids={"trakt": 1388},
                ),
            )
        ]

        result = ProgressFormatters.format_playback_progress(items)

        assert "## Episodes" in result
        assert "Breaking Bad - S01E05" in result
        assert "Gray Matter" in result
        assert "Progress: 23.7%" in result

    def test_format_playback_progress_multiple_items(self) -> None:
        """Test playback progress with multiple items."""
        items = [
            PlaybackProgressResponse(
                progress=45.5,
                paused_at="2024-01-20T15:30:00.000Z",
                id=12345,
                type="movie",
                movie=PlaybackMovieInfo(
                    title="Inception", year=2010, ids={"trakt": 16662}
                ),
            ),
            PlaybackProgressResponse(
                progress=23.7,
                paused_at="2024-01-21T20:00:00.000Z",
                id=67890,
                type="episode",
                episode=PlaybackEpisodeInfo(
                    season=1,
                    number=5,
                    title="Gray Matter",
                    ids={"trakt": 62089},
                ),
                show=PlaybackShowInfo(
                    title="Breaking Bad", year=2008, ids={"trakt": 1388}
                ),
            ),
        ]

        result = ProgressFormatters.format_playback_progress(items)

        assert "# Playback Progress (2 items)" in result
        assert "## Movies" in result
        assert "## Episodes" in result

    def test_format_show_progress_verbose_mode(self) -> None:
        """Test verbose mode shows episode-by-episode watch dates."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=5,
            completed=3,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[
                SeasonProgressResponse(
                    number=1,
                    aired=5,
                    completed=3,
                    episodes=[
                        EpisodeProgressResponse(
                            number=1,
                            completed=True,
                            last_watched_at="2024-01-13T19:00:00.000Z",
                        ),
                        EpisodeProgressResponse(
                            number=2,
                            completed=True,
                            last_watched_at="2024-01-14T20:00:00.000Z",
                        ),
                        EpisodeProgressResponse(
                            number=3,
                            completed=True,
                            last_watched_at="2024-01-15T20:30:00.000Z",
                        ),
                        EpisodeProgressResponse(
                            number=4, completed=False, last_watched_at=None
                        ),
                        EpisodeProgressResponse(
                            number=5, completed=False, last_watched_at=None
                        ),
                    ],
                )
            ],
        )

        result = ProgressFormatters.format_show_progress(
            progress, "test-show", verbose=True
        )

        assert "### Season 1" in result
        assert "**Progress:** 3/5 (60%)" in result
        assert "[x] **E01**" in result
        assert "Watched: 2024-01-13" in result
        assert "[x] **E02**" in result
        assert "[x] **E03**" in result
        assert "[ ] **E04**" in result
        assert "Not watched" in result

    def test_format_show_progress_verbose_mode_no_watch_dates(self) -> None:
        """Test verbose mode handles episodes without watch dates gracefully."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=3,
            completed=2,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[
                SeasonProgressResponse(
                    number=1,
                    aired=3,
                    completed=2,
                    episodes=[
                        EpisodeProgressResponse(
                            number=1,
                            completed=True,
                            last_watched_at=None,
                        ),  # Watched but no date
                        EpisodeProgressResponse(
                            number=2,
                            completed=True,
                            last_watched_at="2024-01-14T20:00:00.000Z",
                        ),
                        EpisodeProgressResponse(
                            number=3, completed=False, last_watched_at=None
                        ),
                    ],
                )
            ],
        )

        result = ProgressFormatters.format_show_progress(
            progress, "test-show", verbose=True
        )

        assert "[x] **E01** - Watched" in result
        assert "[x] **E02** - Watched: 2024-01-14" in result
        assert "[ ] **E03** - Not watched" in result

    def test_format_show_progress_verbose_false_is_compact(self) -> None:
        """Test that verbose=False (default) uses compact format."""
        progress = ShowProgressResponse(  # type: ignore[call-arg]
            aired=5,
            completed=3,
            last_watched_at="2024-01-15T20:30:00.000Z",
            seasons=[
                SeasonProgressResponse(
                    number=1,
                    aired=5,
                    completed=3,
                    episodes=[
                        EpisodeProgressResponse(
                            number=1,
                            completed=True,
                            last_watched_at="2024-01-13T19:00:00.000Z",
                        ),
                        EpisodeProgressResponse(
                            number=2,
                            completed=True,
                            last_watched_at="2024-01-14T20:00:00.000Z",
                        ),
                        EpisodeProgressResponse(
                            number=3, completed=True, last_watched_at=None
                        ),
                        EpisodeProgressResponse(
                            number=4, completed=False, last_watched_at=None
                        ),
                        EpisodeProgressResponse(
                            number=5, completed=False, last_watched_at=None
                        ),
                    ],
                )
            ],
        )

        result = ProgressFormatters.format_show_progress(
            progress, "test-show", verbose=False
        )

        assert "- **Season 1:** 3/5 (60%)" in result
        assert "[x]" not in result
        assert "[ ]" not in result
        assert "E01" not in result
