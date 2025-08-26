"""Episode models for the Trakt MCP server."""

from pydantic import BaseModel


class TraktEpisode(BaseModel):
    """Represents a Trakt episode."""

    season: int
    number: int
    title: str | None = None
    ids: dict[str, str | int | None] | None = None
    last_watched_at: str | None = None
