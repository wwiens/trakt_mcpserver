"""Tests for sync history formatters."""

from models.formatters.sync_history import SyncHistoryFormatters
from models.sync.history import (
    HistoryEpisodeInfo,
    HistoryMovieInfo,
    HistoryNotFound,
    HistoryShowInfo,
    HistorySummary,
    HistorySummaryCount,
    TraktHistoryItem,
    WatchHistoryItem,
)


class TestSyncHistoryFormatters:
    """Tests for SyncHistoryFormatters class."""

    def test_format_watch_history_empty(self) -> None:
        """Test formatting empty watch history."""
        result = SyncHistoryFormatters.format_watch_history([])

        assert "# Watch History" in result
        assert "No items in watch history" in result

    def test_format_watch_history_empty_movies(self) -> None:
        """Test formatting empty movies watch history."""
        result = SyncHistoryFormatters.format_watch_history([], query_type="movies")

        assert "No movies in watch history" in result

    def test_format_watch_history_movies(self) -> None:
        """Test formatting watch history with movies."""
        items = [
            WatchHistoryItem(
                id=123456,
                watched_at="2024-01-15T20:30:00.000Z",
                action="watch",
                type="movie",
                movie=HistoryMovieInfo(
                    title="Inception",
                    year=2010,
                    ids={"trakt": 16662},
                ),
            )
        ]

        result = SyncHistoryFormatters.format_watch_history(items)

        assert "# Watch History (1 item)" in result
        assert "## Movies" in result
        assert "Inception (2010)" in result
        assert "2024-01-15" in result

    def test_format_watch_history_episodes(self) -> None:
        """Test formatting watch history with episodes."""
        items = [
            WatchHistoryItem(
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
        ]

        result = SyncHistoryFormatters.format_watch_history(items)

        assert "## Episodes" in result
        assert "Breaking Bad - S01E01" in result
        assert "Pilot" in result

    def test_format_watch_history_specific_item_not_watched(self) -> None:
        """Test formatting when specific item has not been watched."""
        result = SyncHistoryFormatters.format_watch_history(
            [],
            query_type="movies",
            item_id="16662",
        )

        assert "# Watch History: 16662" in result
        assert "not been watched" in result

    def test_format_watch_history_specific_item_watched(self) -> None:
        """Test formatting when specific item has been watched."""
        items = [
            WatchHistoryItem(
                id=123456,
                watched_at="2024-01-15T20:30:00.000Z",
                action="watch",
                type="movie",
                movie=HistoryMovieInfo(
                    title="Inception",
                    year=2010,
                    ids={"trakt": 16662},
                ),
            ),
            WatchHistoryItem(
                id=123458,
                watched_at="2024-01-20T18:00:00.000Z",
                action="watch",
                type="movie",
                movie=HistoryMovieInfo(
                    title="Inception",
                    year=2010,
                    ids={"trakt": 16662},
                ),
            ),
        ]

        result = SyncHistoryFormatters.format_watch_history(
            items,
            query_type="movies",
            item_id="16662",
        )

        assert "# Watch History: Inception (2010)" in result
        assert "Watched 2 times" in result
        assert "## Watch Events" in result

    def test_format_history_summary_added(self) -> None:
        """Test formatting history add operation summary."""
        summary = HistorySummary(
            added=HistorySummaryCount(movies=2, shows=0, seasons=0, episodes=0),
            not_found=HistoryNotFound(movies=[], shows=[], seasons=[], episodes=[]),
        )

        result = SyncHistoryFormatters.format_history_summary(
            summary, "added", "movies"
        )

        assert "# History Added - Movies" in result
        assert "Successfully added **2** movies" in result

    def test_format_history_summary_removed(self) -> None:
        """Test formatting history remove operation summary."""
        summary = HistorySummary(
            deleted=HistorySummaryCount(movies=1, shows=0, seasons=0, episodes=0),
            not_found=HistoryNotFound(movies=[], shows=[], seasons=[], episodes=[]),
        )

        result = SyncHistoryFormatters.format_history_summary(
            summary, "removed", "movies"
        )

        assert "# History Removed - Movies" in result
        assert "Successfully removed **1** movies" in result

    def test_format_history_summary_nothing_added(self) -> None:
        """Test formatting when nothing was added."""
        summary = HistorySummary(
            added=HistorySummaryCount(movies=0, shows=0, seasons=0, episodes=0),
            not_found=HistoryNotFound(movies=[], shows=[], seasons=[], episodes=[]),
        )

        result = SyncHistoryFormatters.format_history_summary(
            summary, "added", "movies"
        )

        assert "No movies were added" in result

    def test_format_history_summary_not_found(self) -> None:
        """Test formatting when items were not found."""
        summary = HistorySummary(
            added=HistorySummaryCount(movies=0, shows=0, seasons=0, episodes=0),
            not_found=HistoryNotFound(
                movies=[
                    TraktHistoryItem(title="Unknown Movie", year=2024),
                    TraktHistoryItem(ids={"imdb": "tt9999999"}),
                ],
                shows=[],
                seasons=[],
                episodes=[],
            ),
        )

        result = SyncHistoryFormatters.format_history_summary(
            summary, "added", "movies"
        )

        assert "## Items Not Found (2)" in result
        assert "Unknown Movie (2024)" in result
        assert "imdb: tt9999999" in result
        assert "could not be found on Trakt" in result

    def test_format_history_summary_mixed_types(self) -> None:
        """Test formatting summary with multiple types added."""
        summary = HistorySummary(
            added=HistorySummaryCount(movies=2, shows=1, seasons=0, episodes=3),
            not_found=HistoryNotFound(movies=[], shows=[], seasons=[], episodes=[]),
        )

        result = SyncHistoryFormatters.format_history_summary(
            summary, "added", "movies"
        )

        # Should show breakdown when multiple types
        assert "### Breakdown by Type" in result
        assert "Movies: 2" in result
        assert "Shows: 1" in result
        assert "Episodes: 3" in result
