"""TypedDict definitions for test data to ensure type safety in model tests."""

from datetime import datetime
from typing import Literal, NotRequired, TypedDict


class ShowTestData(TypedDict):
    """Type definition for show test data."""

    title: str
    year: int
    ids: dict[str, str | int | None]
    overview: NotRequired[str | None]


class MovieTestData(TypedDict):
    """Type definition for movie test data."""

    title: str
    year: int
    ids: dict[str, str | int | None]
    overview: NotRequired[str | None]


class EpisodeTestData(TypedDict):
    """Type definition for episode test data."""

    season: int
    number: int
    title: NotRequired[str | None]
    ids: NotRequired[dict[str, str | int | None] | None]
    last_watched_at: NotRequired[str | None]


class DeviceCodeTestData(TypedDict):
    """Type definition for device code test data."""

    device_code: str
    user_code: str
    verification_url: str
    expires_in: int
    interval: int


class AuthTokenTestData(TypedDict):
    """Type definition for auth token test data."""

    access_token: str
    refresh_token: str
    expires_in: int
    created_at: int
    scope: str
    token_type: str


class SyncRatingTestData(TypedDict):
    """Type definition for sync rating test data."""

    rated_at: datetime
    rating: int
    type: Literal["movie", "show", "season", "episode"]
    movie: NotRequired[dict[str, str | int | None | dict[str, str | int | None]] | None]
    show: NotRequired[dict[str, str | int | None | dict[str, str | int | None]] | None]
    season: NotRequired[
        dict[str, str | int | None | dict[str, str | int | None]] | None
    ]
    episode: NotRequired[
        dict[str, str | int | None | dict[str, str | int | None]] | None
    ]


class SyncRatingItemTestData(TypedDict):
    """Type definition for sync rating item test data."""

    rating: NotRequired[int | None]
    rated_at: NotRequired[datetime | None]
    title: NotRequired[str | None]
    year: NotRequired[int | None]
    ids: NotRequired[dict[str, str | int | None] | None]


class SyncRatingsSummaryTestData(TypedDict):
    """Type definition for sync ratings summary test data."""

    added: NotRequired[dict[str, int] | None]
    removed: NotRequired[dict[str, int] | None]
    not_found: dict[
        str, list[dict[str, str | int | None | dict[str, str | int | None]]]
    ]


class TrendingShowTestData(TypedDict):
    """Type definition for trending show test data."""

    watchers: int
    show: ShowTestData


class TrendingMovieTestData(TypedDict):
    """Type definition for trending movie test data."""

    watchers: int
    movie: MovieTestData


class PopularShowTestData(TypedDict):
    """Type definition for popular show test data."""

    show: ShowTestData


class PopularMovieTestData(TypedDict):
    """Type definition for popular movie test data."""

    movie: MovieTestData


class SeasonEpisodeData(TypedDict):
    """Type definition for season episode data."""

    number: int
    completed: NotRequired[bool]
    plays: NotRequired[int]
    last_watched_at: NotRequired[str]


class SeasonData(TypedDict):
    """Type definition for season data."""

    number: int
    episodes: list[SeasonEpisodeData]
    aired: NotRequired[int]
    completed: NotRequired[int]


class UserShowTestData(TypedDict):
    """Type definition for user show test data."""

    show: ShowTestData
    last_watched_at: str
    last_updated_at: str
    plays: int
    seasons: NotRequired[list[SeasonData] | None]
