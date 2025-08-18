"""User-related models for the Trakt MCP server."""

from pydantic import BaseModel

from ..shows import TraktShow
from ..types import UserWatchedSeason


class TraktUserShow(BaseModel):
    """Represents a show watched by a user."""

    show: TraktShow
    last_watched_at: str
    last_updated_at: str
    seasons: list[UserWatchedSeason] | None = None
    plays: int
