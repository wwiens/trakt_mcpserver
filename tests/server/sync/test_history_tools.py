"""Tests for sync history helper functions in server.sync.tools."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from models.sync.history import (
    HistoryNotFound,
    HistorySummary,
    HistorySummaryCount,
    TraktHistoryItem,
    TraktHistoryRequest,
)
from models.types.ids import TraktIds
from server.sync.tools import (
    _aggregate_summary,  # pyright: ignore[reportPrivateUsage]
    _batch_show_history_op,  # pyright: ignore[reportPrivateUsage]
    _get_show_season_ids,  # pyright: ignore[reportPrivateUsage]
)

# --- _aggregate_summary tests ---


class TestAggregateSummary:
    """Tests for the _aggregate_summary helper."""

    def test_sums_added_counts(self) -> None:
        """Added counts from source are summed into target."""
        target = HistorySummary(
            added=HistorySummaryCount(movies=1, episodes=3),
        )
        source = HistorySummary(
            added=HistorySummaryCount(movies=2, episodes=5),
        )

        _aggregate_summary(target, source, "added")

        assert target.added is not None
        assert target.added.movies == 3
        assert target.added.episodes == 8
        assert target.added.shows == 0
        assert target.added.seasons == 0

    def test_creates_target_counts_when_none(self) -> None:
        """Target gets counts created when its operation field is None."""
        target = HistorySummary()
        source = HistorySummary(
            added=HistorySummaryCount(movies=2, seasons=1),
        )

        _aggregate_summary(target, source, "added")

        assert target.added is not None
        assert target.added.movies == 2
        assert target.added.seasons == 1

    def test_noop_when_source_counts_none(self) -> None:
        """No changes when source operation field is None."""
        target = HistorySummary(
            added=HistorySummaryCount(movies=5),
        )
        source = HistorySummary()

        _aggregate_summary(target, source, "added")

        assert target.added is not None
        assert target.added.movies == 5

    def test_deleted_operation(self) -> None:
        """Works with the deleted operation field."""
        target = HistorySummary(
            deleted=HistorySummaryCount(episodes=10),
        )
        source = HistorySummary(
            deleted=HistorySummaryCount(episodes=7),
        )

        _aggregate_summary(target, source, "deleted")

        assert target.deleted is not None
        assert target.deleted.episodes == 17

    def test_extends_not_found_lists(self) -> None:
        """Not-found items from source are appended to target."""
        target = HistorySummary(
            added=HistorySummaryCount(movies=1),
            not_found=HistoryNotFound(
                movies=[TraktHistoryItem(title="A")],
                shows=[],
                seasons=[],
                episodes=[],
            ),
        )
        source = HistorySummary(
            added=HistorySummaryCount(movies=1),
            not_found=HistoryNotFound(
                movies=[TraktHistoryItem(title="B")],
                shows=[],
                seasons=[],
                episodes=[],
            ),
        )

        _aggregate_summary(target, source, "added")

        assert len(target.not_found.movies) == 2
        assert target.not_found.movies[0].title == "A"
        assert target.not_found.movies[1].title == "B"


# --- _get_show_season_ids tests ---


class TestGetShowSeasonIds:
    """Tests for the _get_show_season_ids helper."""

    @pytest.mark.asyncio
    async def test_excludes_specials(self) -> None:
        """Season 0 (specials) is excluded from the result."""
        mock_seasons = [
            {"number": 0, "ids": {"trakt": 100}},
            {"number": 1, "ids": {"trakt": 101}},
            {"number": 2, "ids": {"trakt": 102}},
            {"number": 3, "ids": {"trakt": 103}},
        ]

        with patch("server.sync.tools.ShowSeasonsClient") as mock_cls:
            mock_cls.return_value.get_seasons = AsyncMock(return_value=mock_seasons)
            result = await _get_show_season_ids("breaking-bad")

        assert result == [101, 102, 103]

    @pytest.mark.asyncio
    async def test_empty_seasons(self) -> None:
        """Returns empty list when show has no seasons."""
        with patch("server.sync.tools.ShowSeasonsClient") as mock_cls:
            mock_cls.return_value.get_seasons = AsyncMock(return_value=[])
            result = await _get_show_season_ids("some-show")

        assert result == []


# --- _batch_show_history_op tests ---


def _make_summary(operation: str, episodes: int = 0) -> HistorySummary:
    """Create a simple HistorySummary with a count."""
    counts = HistorySummaryCount(episodes=episodes)
    summary = HistorySummary()
    setattr(summary, operation, counts)
    return summary


class TestBatchShowHistoryOp:
    """Tests for the _batch_show_history_op helper."""

    @pytest.mark.asyncio
    async def test_splits_by_season(self) -> None:
        """Show is split into per-season requests and results aggregated."""
        client_method = AsyncMock(
            side_effect=[
                _make_summary("added", episodes=10),
                _make_summary("added", episodes=8),
                _make_summary("added", episodes=12),
            ]
        )
        show_item = TraktHistoryItem(ids=TraktIds(trakt=1390))

        with patch(
            "server.sync.tools._get_show_season_ids",
            new_callable=AsyncMock,
            return_value=[201, 202, 203],
        ):
            result = await _batch_show_history_op(client_method, [show_item], "added")

        assert client_method.call_count == 3
        assert result.added is not None
        assert result.added.episodes == 30

    @pytest.mark.asyncio
    async def test_no_resolvable_id_sends_as_show(self) -> None:
        """Item with no IDs is sent as a single show request."""
        client_method = AsyncMock(return_value=_make_summary("added", episodes=5))
        show_item = TraktHistoryItem(ids=None, title="Mystery Show")

        result = await _batch_show_history_op(client_method, [show_item], "added")

        client_method.assert_called_once()
        call_request: TraktHistoryRequest = client_method.call_args[0][0]
        assert call_request.shows is not None
        assert call_request.shows[0].title == "Mystery Show"
        assert result.added is not None
        assert result.added.episodes == 5

    @pytest.mark.asyncio
    async def test_slug_fallback(self) -> None:
        """Uses slug when trakt ID is absent."""
        client_method = AsyncMock(return_value=_make_summary("deleted", episodes=6))
        show_item = TraktHistoryItem(ids=TraktIds(slug="breaking-bad"))

        with patch(
            "server.sync.tools._get_show_season_ids",
            new_callable=AsyncMock,
            return_value=[301],
        ) as mock_get_ids:
            result = await _batch_show_history_op(client_method, [show_item], "deleted")

        mock_get_ids.assert_called_once_with("breaking-bad")
        assert result.deleted is not None
        assert result.deleted.episodes == 6

    @pytest.mark.asyncio
    async def test_season_fetch_failure_falls_back(self) -> None:
        """Falls back to single show request when season fetch fails."""
        client_method = AsyncMock(return_value=_make_summary("added", episodes=50))
        show_item = TraktHistoryItem(ids=TraktIds(trakt=1390))

        with patch(
            "server.sync.tools._get_show_season_ids",
            new_callable=AsyncMock,
            side_effect=RuntimeError("API failure"),
        ):
            result = await _batch_show_history_op(client_method, [show_item], "added")

        client_method.assert_called_once()
        call_request: TraktHistoryRequest = client_method.call_args[0][0]
        assert call_request.shows is not None
        assert result.added is not None
        assert result.added.episodes == 50

    @pytest.mark.asyncio
    async def test_multiple_shows_aggregated(self) -> None:
        """Multiple show items are each processed and aggregated."""
        client_method = AsyncMock(
            side_effect=[
                _make_summary("added", episodes=10),
                _make_summary("added", episodes=20),
            ]
        )
        items = [
            TraktHistoryItem(ids=TraktIds(trakt=100)),
            TraktHistoryItem(ids=TraktIds(trakt=200)),
        ]

        with patch(
            "server.sync.tools._get_show_season_ids",
            new_callable=AsyncMock,
            # Each show has 1 season
            side_effect=[[501], [502]],
        ):
            result = await _batch_show_history_op(client_method, items, "added")

        assert client_method.call_count == 2
        assert result.added is not None
        assert result.added.episodes == 30

    @pytest.mark.asyncio
    async def test_partial_season_failure_continues(self) -> None:
        """If one season request fails, remaining seasons still proceed."""
        client_method = AsyncMock(
            side_effect=[
                _make_summary("deleted", episodes=10),
                RuntimeError("504 timeout"),
                _make_summary("deleted", episodes=12),
            ]
        )
        show_item = TraktHistoryItem(ids=TraktIds(trakt=92))

        with patch(
            "server.sync.tools._get_show_season_ids",
            new_callable=AsyncMock,
            return_value=[301, 302, 303],
        ):
            result = await _batch_show_history_op(client_method, [show_item], "deleted")

        assert client_method.call_count == 3
        assert result.deleted is not None
        assert result.deleted.episodes == 22
