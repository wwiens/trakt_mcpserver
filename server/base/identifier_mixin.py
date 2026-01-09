"""Mixin for Trakt identifier validation in Pydantic models."""

import re
from typing import ClassVar, Self

from pydantic import BaseModel, Field, field_validator, model_validator


class IdentifierValidatorMixin(BaseModel):
    """Mixin that validates Trakt identifiers.

    This mixin provides field and model validators for common Trakt identifier fields.
    It validates:
    - trakt_id: Must be numeric
    - tmdb_id: Must be numeric
    - tvdb_id: Must be numeric
    - imdb_id: Must match tt + digits format (e.g., tt0372784)
    - slug: Any non-empty string
    - At least one identifier OR both title+year must be provided

    Classes using this mixin must define these fields:
        - trakt_id: str | None
        - slug: str | None
        - imdb_id: str | None
        - tmdb_id: str | None
        - tvdb_id: str | None
        - title: str | None
        - year: int | None

    Classes can customize the error message by setting:
        - _identifier_error_prefix: ClassVar[str] = "Item"
    """

    # Fields with default values for mixin compatibility
    trakt_id: str | None = Field(default=None, min_length=1, description="Trakt ID")
    slug: str | None = Field(default=None, min_length=1, description="Trakt slug")
    imdb_id: str | None = Field(default=None, min_length=1, description="IMDB ID")
    tmdb_id: str | None = Field(default=None, min_length=1, description="TMDB ID")
    tvdb_id: str | None = Field(default=None, min_length=1, description="TVDB ID")
    title: str | None = Field(default=None, min_length=1, description="Title")
    year: int | None = Field(default=None, gt=1800, description="Release year")

    # Class variable for customizable error message prefix
    _identifier_error_prefix: ClassVar[str] = "Item"

    @field_validator(
        "trakt_id", "slug", "imdb_id", "tmdb_id", "tvdb_id", "title", mode="before"
    )
    @classmethod
    def _strip_strings(cls, v: object) -> object:
        """Strip whitespace from string fields."""
        return v.strip() if isinstance(v, str) else v

    @field_validator("trakt_id", mode="after")
    @classmethod
    def _validate_trakt_id_numeric(cls, v: str | None) -> str | None:
        """Ensure trakt_id is numeric if provided."""
        if v is not None and not v.isdigit():
            raise ValueError(f"trakt_id must be numeric, got: '{v}'")
        return v

    @field_validator("tmdb_id", mode="after")
    @classmethod
    def _validate_tmdb_id_numeric(cls, v: str | None) -> str | None:
        """Ensure tmdb_id is numeric if provided."""
        if v is not None and not v.isdigit():
            raise ValueError(f"tmdb_id must be numeric, got: '{v}'")
        return v

    @field_validator("tvdb_id", mode="after")
    @classmethod
    def _validate_tvdb_id_numeric(cls, v: str | None) -> str | None:
        """Ensure tvdb_id is numeric if provided."""
        if v is not None and not v.isdigit():
            raise ValueError(f"tvdb_id must be numeric, got: '{v}'")
        return v

    @field_validator("imdb_id", mode="after")
    @classmethod
    def _validate_imdb_id_format(cls, v: str | None) -> str | None:
        """Ensure imdb_id follows tt + digits format if provided."""
        if v is not None and not re.match(r"^tt\d+$", v):
            raise ValueError(
                f"imdb_id must be in format 'tt' followed by digits (e.g., 'tt0372784'), got: '{v}'"
            )
        return v

    @model_validator(mode="after")
    def _validate_identifiers(self) -> Self:
        """Ensure at least one identifier OR both title+year are provided."""
        has_id = any(
            [self.trakt_id, self.slug, self.imdb_id, self.tmdb_id, self.tvdb_id]
        )
        has_title_year = self.title and self.year

        if not has_id and not has_title_year:
            prefix = self._identifier_error_prefix
            raise ValueError(
                f"{prefix} must include either an identifier (trakt_id, slug, imdb_id, tmdb_id, or tvdb_id) "
                + "or both title and year for proper identification"
            )
        return self
