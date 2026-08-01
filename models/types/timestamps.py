"""Timestamp value types for Trakt sync endpoints.

Trakt's ``POST /sync/history`` accepts two sentinel strings in place of a UTC
timestamp: ``released`` uses the initial release date plus runtime (episodes
only), and ``unknown`` marks the item watched without a specific date. The
Trakt OpenAPI schema types this field as a plain nullable string.
"""

from datetime import datetime
from typing import Literal

WatchedAtSentinel = Literal["released", "unknown"]

WatchedAtValue = datetime | WatchedAtSentinel
