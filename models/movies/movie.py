"""Movie models for the Trakt MCP server."""

from typing import Any

from pydantic import BaseModel, Field


class TraktMovie(BaseModel):
    """Represents a Trakt movie."""

    title: str
    year: int | None = None
    ids: dict[str, str] = Field(
        description="Various IDs for the movie (trakt, slug, tmdb, imdb)"
    )
    overview: str | None = None


class TraktTrendingMovie(BaseModel):
    """Represents a trending movie from Trakt API."""

    watchers: int = Field(description="Number of people watching this movie")
    movie: TraktMovie


class TraktPopularMovie(BaseModel):
    """Represents a popular movie from Trakt API."""

    movie: TraktMovie = Field(description="The movie information")

    @classmethod
    def from_api_response(cls, api_data: dict[str, Any]) -> "TraktPopularMovie":
        """Create a TraktPopularMovie instance from raw API data."""
        return cls(movie=TraktMovie(**api_data))
