"""Shared watchlist-shaped inputs for personal collection mutations."""

from typing import ClassVar

from pydantic import Field, field_validator

from server.base import IdentifierValidatorMixin


class UserWatchlistRequestItem(IdentifierValidatorMixin):
    """Single watchlist item for add operations (with optional notes)."""

    _identifier_error_prefix: ClassVar[str] = "Watchlist item"

    notes: str | None = Field(
        default=None,
        max_length=500,
        description="Optional notes (VIP only, 500 char max)",
    )

    @field_validator("notes", mode="before")
    @classmethod
    def _strip_notes(cls, v: object) -> object:
        """Strip whitespace from notes field."""
        return v.strip() if isinstance(v, str) else v


class UserWatchlistIdentifier(IdentifierValidatorMixin):
    """Watchlist item identifier for removal operations (no notes)."""

    _identifier_error_prefix: ClassVar[str] = "Watchlist item"
