"""Episode models for the Trakt MCP server."""

from pydantic import BaseModel

from models.types.ids import TraktIds


class TraktEpisode(BaseModel):
    """Represents a Trakt episode."""

    season: int
    number: int
    title: str | None = None
    ids: TraktIds | None = None
    last_watched_at: str | None = None
