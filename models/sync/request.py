"""Sync request models for the Trakt MCP server."""

from pydantic import BaseModel, ConfigDict

from .base import TraktSyncRatingItem


class TraktSyncRatingsRequest(BaseModel):
    """Request structure for POST/DELETE sync ratings operations."""

    # Reject unknown fields to avoid silent payload issues
    model_config = ConfigDict(extra="forbid")

    movies: list[TraktSyncRatingItem] | None = None
    shows: list[TraktSyncRatingItem] | None = None
    seasons: list[TraktSyncRatingItem] | None = None
    episodes: list[TraktSyncRatingItem] | None = None

    def _non_empty_lists(self) -> list[str]:
        present: list[str] = []
        for name in ("movies", "shows", "seasons", "episodes"):
            items = getattr(self, name)
            if items:
                present.append(name)
        return present

    def model_post_init(self, __context: dict[str, object] | None) -> None:
        """Validate that exactly one non-empty ratings list is provided."""
        present = self._non_empty_lists()
        if len(present) == 0:
            raise ValueError("At least one ratings list must be provided")
        if len(present) > 1:
            raise ValueError(
                f"Only one ratings list allowed per request, got: {', '.join(present)}"
            )
