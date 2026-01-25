"""Show progress models for the Trakt MCP server."""

from typing import NotRequired, TypedDict


class EpisodeProgressResponse(TypedDict):
    """Episode progress response from Trakt API."""

    number: int
    completed: bool
    last_watched_at: str | None


class SeasonProgressResponse(TypedDict):
    """Season progress response from Trakt API."""

    number: int
    title: NotRequired[str]
    aired: int
    completed: int
    episodes: list[EpisodeProgressResponse]


class HiddenSeasonResponse(TypedDict):
    """Hidden season response from Trakt API."""

    number: int
    ids: dict[str, str | int | None]


class EpisodeInfo(TypedDict):
    """Episode information for next/last episode."""

    season: int
    number: int
    title: str | None
    ids: dict[str, str | int | None]


class ShowProgressResponse(TypedDict):
    """Show watched progress response from Trakt API."""

    aired: int
    completed: int
    last_watched_at: str | None
    reset_at: NotRequired[str | None]
    seasons: list[SeasonProgressResponse]
    hidden_seasons: NotRequired[list[HiddenSeasonResponse]]
    next_episode: NotRequired[EpisodeInfo | None]
    last_episode: NotRequired[EpisodeInfo | None]
