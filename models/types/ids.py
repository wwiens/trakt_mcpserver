"""Trakt ID type definitions and validation."""

import re

from pydantic import BaseModel, field_validator


class TraktIds(BaseModel):
    """Validated Trakt ID structure for API responses.

    All fields are optional since API responses may include different
    combinations of IDs depending on the resource type.
    """

    trakt: int | None = None
    slug: str | None = None
    imdb: str | None = None
    tmdb: int | None = None
    tvdb: int | None = None

    @field_validator("trakt", "tmdb", "tvdb", mode="before")
    @classmethod
    def coerce_to_int(cls, v: object) -> int | None:
        """Coerce string numeric values to positive integers."""
        if v is None:
            return None
        if isinstance(v, int):
            if v <= 0:
                raise ValueError(f"Expected positive integer, got: {v}")
            return v
        if isinstance(v, str) and v.isdigit():
            result = int(v)
            if result <= 0:
                raise ValueError(f"Expected positive integer, got: {result}")
            return result
        raise ValueError(f"Expected positive integer or numeric string, got: {v!r}")

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug(cls, v: object) -> str | None:
        """Validate slug format (lowercase alphanumerics and hyphens)."""
        if v is None:
            return None
        if isinstance(v, str):
            if re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
                return v
            raise ValueError(f"slug must match ^[a-z0-9]+(?:-[a-z0-9]+)*$, got: {v!r}")
        raise ValueError(f"slug must be a string, got: {type(v).__name__}")

    @field_validator("imdb", mode="before")
    @classmethod
    def validate_imdb_format(cls, v: object) -> str | None:
        """Validate IMDB ID format (tt + digits)."""
        if v is None:
            return None
        if isinstance(v, str):
            if re.match(r"^tt\d+$", v):
                return v
            raise ValueError(f"imdb must match ^tt\\d+$, got: {v!r}")
        raise ValueError(f"imdb must be a string, got: {type(v).__name__}")
