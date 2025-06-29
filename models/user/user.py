"""User-related models for the Trakt MCP server."""

from typing import Any

from pydantic import BaseModel

from ..shows import TraktShow


class TraktUserShow(BaseModel):
    """Represents a show watched by a user."""

    show: TraktShow
    last_watched_at: str
    last_updated_at: str
    seasons: list[dict[str, Any]] | None = None
    plays: int
