"""Timestamp value types for Trakt sync endpoints.

Trakt's ``POST /sync/history`` accepts two sentinel strings in place of a UTC
timestamp: ``released`` uses the initial release date plus runtime (episodes
only), and ``unknown`` marks the item watched without a specific date. The
Trakt OpenAPI schema types this field as a plain nullable string.
"""

from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime


def _normalize_to_utc(value: datetime) -> datetime:
    """Convert an offset-aware datetime to UTC.

    Trakt documents ``watched_at`` as a UTC datetime, so an offset-aware value
    is retimed rather than sent with its original offset. Naive values are
    rejected upstream by ``AwareDatetime`` because their instant is ambiguous.
    """
    return value.astimezone(UTC)


UtcDatetime = Annotated[AwareDatetime, AfterValidator(_normalize_to_utc)]

WatchedAtSentinel = Literal["released", "unknown"]

WatchedAtValue = UtcDatetime | WatchedAtSentinel
