"""Checkin models for the Trakt MCP server."""

from typing import Any

from pydantic import BaseModel, Field


class TraktCheckin(BaseModel):
    """Represents a Trakt checkin response."""

    id: int = Field(description="The checkin ID")
    watched_at: str = Field(description="When the item was watched")
    sharing: dict[str, bool] = Field(
        description="Social sharing settings", default_factory=dict
    )
    show: dict[str, Any] | None = Field(
        default=None, description="Show information if checking in to a show"
    )
    episode: dict[str, Any] | None = Field(
        default=None, description="Episode information if checking in to an episode"
    )
    movie: dict[str, Any] | None = Field(
        default=None, description="Movie information if checking in to a movie"
    )

    @classmethod
    def from_api_response(cls, api_data: dict[str, Any]) -> "TraktCheckin":
        """Create a TraktCheckin instance from raw API data."""
        return cls(**api_data)
