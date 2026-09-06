"""Tests for sync history models."""

from datetime import UTC, datetime, timedelta, timezone
from typing import Final

import pytest
from pydantic import ValidationError

from models.sync.history import (
    HistoryNotFound,
    TraktHistoryItem,
    TraktHistoryRequest,
)
from models.types.ids import TraktIds
from models.types.timestamps import WatchedAtSentinel

SENTINELS: Final[tuple[WatchedAtSentinel, ...]] = ("released", "unknown")


class TestWatchedAtValidation:
    """Validation of the watched_at union on TraktHistoryItem."""

    def test_accepts_iso_string(self) -> None:
        """ISO 8601 strings coerce to datetime."""
        item = TraktHistoryItem.model_validate(
            {"watched_at": "2024-01-15T20:30:00.000Z"}
        )

        assert isinstance(item.watched_at, datetime)

    def test_accepts_datetime(self) -> None:
        """Native datetime values pass through."""
        moment = datetime.fromisoformat("2024-01-15T20:30:00+00:00")
        item = TraktHistoryItem(watched_at=moment)

        assert item.watched_at == moment

    @pytest.mark.parametrize("sentinel", SENTINELS)
    def test_accepts_sentinel(self, sentinel: WatchedAtSentinel) -> None:
        """Documented sentinels stay strings rather than coercing to datetime."""
        item = TraktHistoryItem(watched_at=sentinel)

        assert item.watched_at == sentinel
        assert not isinstance(item.watched_at, datetime)

    @pytest.mark.parametrize("value", ["Released", "UNKNOWN", "yesterday", ""])
    def test_rejects_arbitrary_string(self, value: str) -> None:
        """Sentinels are case-sensitive and no other string is accepted."""
        with pytest.raises(ValidationError):
            TraktHistoryItem.model_validate({"watched_at": value})

    def test_defaults_to_none(self) -> None:
        """Omitting watched_at leaves it unset."""
        assert TraktHistoryItem().watched_at is None

    @pytest.mark.parametrize(
        "value",
        [
            datetime(2024, 1, 15, 20, 30),
            "2024-01-15T20:30:00",
            "2024-01-15T20:30:00.000",
        ],
    )
    def test_rejects_naive_datetime(self, value: datetime | str) -> None:
        """Trakt documents watched_at as UTC, so an ambiguous instant is invalid."""
        with pytest.raises(ValidationError):
            TraktHistoryItem.model_validate({"watched_at": value})

    @pytest.mark.parametrize(
        "value",
        [
            datetime(2024, 1, 15, 20, 30, tzinfo=timezone(timedelta(hours=5))),
            "2024-01-15T20:30:00+05:00",
        ],
    )
    def test_normalizes_offset_to_utc(self, value: datetime | str) -> None:
        """Offset-aware values are retimed to UTC rather than kept as-is."""
        item = TraktHistoryItem.model_validate({"watched_at": value})

        assert item.watched_at == datetime(2024, 1, 15, 15, 30, tzinfo=UTC)
        assert isinstance(item.watched_at, datetime)
        assert item.watched_at.tzinfo == UTC


class TestWatchedAtSerialization:
    """The outgoing JSON payload built by the sync history client."""

    @pytest.mark.parametrize("sentinel", SENTINELS)
    def test_sentinel_survives_model_dump(self, sentinel: WatchedAtSentinel) -> None:
        """Sentinels must reach Trakt verbatim, not as a coerced timestamp."""
        request = TraktHistoryRequest(
            episodes=[TraktHistoryItem(ids=TraktIds(trakt=62085), watched_at=sentinel)]
        )

        payload = request.model_dump(mode="json", exclude_none=True)

        assert payload["episodes"][0]["watched_at"] == sentinel

    def test_datetime_serialized_as_iso_string(self) -> None:
        """Real timestamps still serialize to ISO 8601."""
        request = TraktHistoryRequest(
            movies=[
                TraktHistoryItem(
                    ids=TraktIds(trakt=16662),
                    watched_at=datetime.fromisoformat("2024-01-15T20:30:00+00:00"),
                )
            ]
        )

        payload = request.model_dump(mode="json", exclude_none=True)

        assert payload["movies"][0]["watched_at"] == "2024-01-15T20:30:00Z"

    def test_offset_datetime_serialized_as_utc(self) -> None:
        """A non-UTC offset must reach Trakt as the equivalent UTC timestamp."""
        request = TraktHistoryRequest(
            movies=[
                TraktHistoryItem(
                    ids=TraktIds(trakt=16662),
                    watched_at=datetime.fromisoformat("2024-01-15T20:30:00+05:00"),
                )
            ]
        )

        payload = request.model_dump(mode="json", exclude_none=True)

        assert payload["movies"][0]["watched_at"] == "2024-01-15T15:30:00Z"

    def test_none_watched_at_is_omitted(self) -> None:
        """An unset watched_at is excluded so Trakt defaults to now."""
        request = TraktHistoryRequest(
            movies=[TraktHistoryItem(ids=TraktIds(trakt=16662))]
        )

        payload = request.model_dump(mode="json", exclude_none=True)

        assert "watched_at" not in payload["movies"][0]


class TestHistoryNotFoundParsing:
    """TraktHistoryItem also parses the not_found block of API responses."""

    @pytest.mark.parametrize("sentinel", SENTINELS)
    def test_parses_sentinel_echoed_by_api(self, sentinel: WatchedAtSentinel) -> None:
        """A sentinel echoed back in not_found must not break response parsing."""
        not_found = HistoryNotFound.model_validate(
            {
                "movies": [{"title": "Missing", "year": 2024, "watched_at": sentinel}],
                "shows": [],
                "seasons": [],
                "episodes": [],
            }
        )

        assert not_found.movies[0].watched_at == sentinel
