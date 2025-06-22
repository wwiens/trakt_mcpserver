"""Show models for the Trakt MCP server."""

from typing import Any

from pydantic import BaseModel, Field


class TraktShow(BaseModel):
    """Represents a Trakt show."""

    title: str
    year: int | None = None
    ids: dict[str, str] = Field(
        description="Various IDs for the show (trakt, slug, tvdb, imdb, tmdb)"
    )
    overview: str | None = None


class TraktTrendingShow(BaseModel):
    """Represents a trending show from Trakt API."""

    watchers: int = Field(description="Number of people watching this show")
    show: TraktShow


class TraktPopularShow(BaseModel):
    """Represents a popular show from Trakt API."""

    show: TraktShow = Field(description="The show information")

    @classmethod
    def from_api_response(cls, api_data: dict[str, Any]) -> "TraktPopularShow":
        """Create a TraktPopularShow instance from raw API data."""
        return cls(show=TraktShow(**api_data))
