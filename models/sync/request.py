"""Sync request models for the Trakt MCP server."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

from .base import TraktSyncRatingItem


class TraktSyncRatingsRequest(BaseModel):
    """Request structure for POST/DELETE sync ratings operations.

    Exactly one of movies, shows, seasons, or episodes must be provided and non-empty.
    """

    # Names of the allowed collections
    FIELDS: ClassVar[tuple[str, ...]] = ("movies", "shows", "seasons", "episodes")

    # Reject unknown fields to avoid silent payload issues
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    movies: list[TraktSyncRatingItem] | None = Field(
        default=None, min_length=1, description="Ratings payload for movies"
    )
    shows: list[TraktSyncRatingItem] | None = Field(
        default=None, min_length=1, description="Ratings payload for shows"
    )
    seasons: list[TraktSyncRatingItem] | None = Field(
        default=None, min_length=1, description="Ratings payload for seasons"
    )
    episodes: list[TraktSyncRatingItem] | None = Field(
        default=None, min_length=1, description="Ratings payload for episodes"
    )

    def _non_empty_lists(self) -> list[str]:
        return [name for name in self.FIELDS if getattr(self, name)]

    @model_validator(mode="after")
    def validate_exactly_one_list(self) -> "TraktSyncRatingsRequest":
        """Validate that exactly one non-empty ratings list is provided."""
        present = self._non_empty_lists()
        if len(present) == 0:
            raise PydanticCustomError(
                "ratings.collection_missing",
                "At least one ratings list must be provided",
            )
        if len(present) > 1:
            raise PydanticCustomError(
                "ratings.multiple_collections",
                "Only one ratings list allowed per request, got: {collections}",
                {"collections": ", ".join(present)},
            )
        return self
