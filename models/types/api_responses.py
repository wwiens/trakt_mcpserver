"""Type definitions for Trakt API responses."""

from typing import Any, Literal, NotRequired, TypedDict

# Video types
VideoSite = Literal["youtube", "vimeo", "dailymotion", "metacafe"]
VideoType = Literal[
    "trailer", "teaser", "featurette", "clip", "behind_the_scenes", "gag_reel"
]


class VideoResponse(TypedDict):
    """Video response from Trakt API."""

    title: str
    url: str
    site: VideoSite
    type: VideoType
    size: int  # 480, 720, 1080, etc.
    official: bool
    published_at: str  # ISO datetime string from API
    country: str  # ISO 3166-1 alpha-2
    language: str  # ISO 639-1


# Base types
class TraktIdsDict(TypedDict):
    """Standard ID structure used in raw API responses (TypedDict)."""

    trakt: int
    slug: str
    imdb: NotRequired[str]
    tmdb: NotRequired[int]
    tvdb: NotRequired[int]


class TraktRating(TypedDict):
    """Rating information."""

    rating: float
    votes: int
    distribution: dict[str, int]


# Show types
class ShowResponse(TypedDict):
    """Complete show data from Trakt API."""

    title: str
    year: int
    ids: TraktIdsDict
    overview: NotRequired[str]
    first_aired: NotRequired[str]
    airs: NotRequired[dict[str, str]]
    runtime: NotRequired[int]
    certification: NotRequired[str]
    network: NotRequired[str]
    country: NotRequired[str]
    trailer: NotRequired[str]
    homepage: NotRequired[str]
    status: NotRequired[str]
    rating: NotRequired[float]
    votes: NotRequired[int]
    comment_count: NotRequired[int]
    updated_at: NotRequired[str]
    language: NotRequired[str]
    available_translations: NotRequired[list[str]]
    genres: NotRequired[list[str]]


class EpisodeResponse(TypedDict):
    """Episode data structure."""

    season: int
    number: int
    title: NotRequired[str]
    ids: TraktIdsDict
    number_abs: NotRequired[int]
    overview: NotRequired[str]
    first_aired: NotRequired[str]
    rating: NotRequired[float]
    votes: NotRequired[int]
    comment_count: NotRequired[int]
    available_translations: NotRequired[list[str]]
    runtime: NotRequired[int]


class SeasonResponse(TypedDict):
    """Season data structure."""

    number: int
    ids: TraktIdsDict
    rating: NotRequired[float]
    votes: NotRequired[int]
    episode_count: NotRequired[int]
    aired_episodes: NotRequired[int]
    title: NotRequired[str]
    overview: NotRequired[str]
    first_aired: NotRequired[str]
    updated_at: NotRequired[str]
    network: NotRequired[str]
    original_title: NotRequired[str]
    episodes: NotRequired[list[EpisodeResponse]]


# Movie types
class MovieResponse(TypedDict):
    """Complete movie data from Trakt API."""

    title: str
    year: int
    ids: TraktIdsDict
    tagline: NotRequired[str]
    overview: NotRequired[str]
    released: NotRequired[str]
    runtime: NotRequired[int]
    country: NotRequired[str]
    trailer: NotRequired[str]
    homepage: NotRequired[str]
    status: NotRequired[str]
    rating: NotRequired[float]
    votes: NotRequired[int]
    comment_count: NotRequired[int]
    updated_at: NotRequired[str]
    language: NotRequired[str]
    available_translations: NotRequired[list[str]]
    languages: NotRequired[list[str]]
    genres: NotRequired[list[str]]
    certification: NotRequired[str]


# User types
class UserResponse(TypedDict):
    """User profile data."""

    username: str
    private: bool
    name: NotRequired[str]
    vip: NotRequired[bool]
    vip_ep: NotRequired[bool]
    ids: dict[str, str]
    joined_at: NotRequired[str]
    location: NotRequired[str]
    about: NotRequired[str]
    gender: NotRequired[str]
    age: NotRequired[int]
    images: NotRequired[dict[str, dict[str, str]]]


# Comment types
class CommentResponse(TypedDict):
    """Comment data structure."""

    id: int
    comment: str
    spoiler: bool
    review: bool
    parent_id: NotRequired[int]
    created_at: str
    updated_at: NotRequired[str]
    replies: NotRequired[int]
    likes: NotRequired[int]
    user_stats: NotRequired[dict[str, int]]
    user: UserResponse


# Auth types
class DeviceCodeResponse(TypedDict):
    """Device code for OAuth flow."""

    device_code: str
    user_code: str
    verification_url: str
    expires_in: int
    interval: int


class TokenResponse(TypedDict):
    """OAuth token response."""

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    created_at: int


# Checkin types
class CheckinResponse(TypedDict):
    """Checkin confirmation data."""

    id: int
    watched_at: str
    sharing: dict[str, bool]
    show: NotRequired[ShowResponse]
    episode: NotRequired[EpisodeResponse]
    movie: NotRequired[MovieResponse]


# Stats types
class StatsResponse(TypedDict):
    """Statistics data."""

    watchers: int
    plays: int
    collectors: int
    comments: NotRequired[int]
    lists: NotRequired[int]
    votes: NotRequired[int]
    favorited: NotRequired[int]


# Wrapper types
class TrendingWrapper(TypedDict):
    """Wrapper for trending items."""

    watchers: int
    show: NotRequired[ShowResponse]
    movie: NotRequired[MovieResponse]


class AnticipatedShowWrapper(TypedDict):
    """Wrapper for anticipated shows data."""

    list_count: int
    show: ShowResponse


class AnticipatedMovieWrapper(TypedDict):
    """Wrapper for anticipated movies data."""

    list_count: int
    movie: MovieResponse


class SearchResult(TypedDict):
    """Search result wrapper."""

    type: str
    score: float
    show: NotRequired[ShowResponse]
    movie: NotRequired[MovieResponse]
    episode: NotRequired[EpisodeResponse]
    person: NotRequired[dict[str, Any]]
    list: NotRequired[dict[str, Any]]


# User watched types
class UserWatchedEpisode(TypedDict):
    """Episode data in user watched shows."""

    number: int
    plays: NotRequired[int]
    last_watched_at: NotRequired[str]


class UserWatchedSeason(TypedDict):
    """Season data in user watched shows."""

    number: int
    episodes: list[UserWatchedEpisode]


# Stats wrapper types
class FavoritedShowWrapper(TypedDict):
    """Wrapper for favorited shows data."""

    user_count: int
    show: ShowResponse


class PlayedShowWrapper(TypedDict):
    """Wrapper for played shows data."""

    watcher_count: int
    play_count: int
    show: ShowResponse


class WatchedShowWrapper(TypedDict):
    """Wrapper for watched shows data."""

    watcher_count: int
    play_count: int
    show: ShowResponse


class FavoritedMovieWrapper(TypedDict):
    """Wrapper for favorited movies data."""

    user_count: int
    movie: MovieResponse


class PlayedMovieWrapper(TypedDict):
    """Wrapper for played movies data."""

    watcher_count: int
    play_count: int
    movie: MovieResponse


class WatchedMovieWrapper(TypedDict):
    """Wrapper for watched movies data."""

    watcher_count: int
    play_count: int
    movie: MovieResponse


class BoxOfficeMovieWrapper(TypedDict):
    """Wrapper for box office movie data."""

    revenue: int
    movie: MovieResponse


# User history types
class UserWatchedShow(TypedDict):
    """User's watched show data."""

    last_watched_at: str
    last_updated_at: str
    plays: int
    show: ShowResponse
    seasons: NotRequired[list[UserWatchedSeason]]


class UserWatchedMovie(TypedDict):
    """User's watched movie data."""

    last_watched_at: str
    plays: int
    movie: MovieResponse


# Translation types
class TranslationResponse(TypedDict):
    """Translation data from Trakt API."""

    title: str
    overview: str
    language: str
    country: str


# People types
class PersonSocialIdsDict(TypedDict):
    """Social media IDs for a person."""

    twitter: NotRequired[str | None]
    facebook: NotRequired[str | None]
    instagram: NotRequired[str | None]
    wikipedia: NotRequired[str | None]


class PersonResponse(TypedDict):
    """Person data from Trakt API."""

    name: str
    ids: TraktIdsDict
    social_ids: NotRequired[PersonSocialIdsDict]
    biography: NotRequired[str | None]
    birthday: NotRequired[str | None]
    death: NotRequired[str | None]
    birthplace: NotRequired[str | None]
    homepage: NotRequired[str | None]
    gender: NotRequired[str | None]
    known_for_department: NotRequired[str | None]
    updated_at: NotRequired[str]


class CastMember(TypedDict):
    """Cast member in a show/season."""

    characters: list[str]
    episode_count: NotRequired[int]
    person: PersonResponse


class CrewMember(TypedDict):
    """Crew member in a show/season."""

    jobs: list[str]
    episode_count: NotRequired[int]
    person: PersonResponse


class PeopleResponse(TypedDict):
    """People (cast and crew) response from Trakt API."""

    cast: list[CastMember]
    crew: NotRequired[dict[str, list[CrewMember]]]
    guest_stars: NotRequired[list[CastMember]]


# Person credit types (for /people/{id}/movies and /people/{id}/shows)
class PersonMovieCastCredit(TypedDict):
    """Cast credit for a person in a movie."""

    characters: list[str]
    movie: MovieResponse


class PersonMovieCrewCredit(TypedDict):
    """Crew credit for a person in a movie."""

    jobs: list[str]
    movie: MovieResponse


class PersonMovieCreditsResponse(TypedDict):
    """Person's movie credits response from Trakt API."""

    cast: list[PersonMovieCastCredit]
    crew: NotRequired[dict[str, list[PersonMovieCrewCredit]]]


class PersonShowCastCredit(TypedDict):
    """Cast credit for a person in a show."""

    characters: list[str]
    episode_count: NotRequired[int]
    series_regular: NotRequired[bool]
    show: ShowResponse


class PersonShowCrewCredit(TypedDict):
    """Crew credit for a person in a show."""

    jobs: list[str]
    episode_count: NotRequired[int]
    show: ShowResponse


class PersonShowCreditsResponse(TypedDict):
    """Person's show credits response from Trakt API."""

    cast: list[PersonShowCastCredit]
    crew: NotRequired[dict[str, list[PersonShowCrewCredit]]]


# Season stats types
class SeasonStatsResponse(TypedDict):
    """Season statistics from Trakt API."""

    watchers: int
    plays: int
    collectors: int
    collected_episodes: int
    comments: int
    lists: int
    votes: int


# List types
class ListUserResponse(TypedDict):
    """User data within a list response."""

    username: str
    private: bool
    name: NotRequired[str]
    vip: NotRequired[bool]
    ids: dict[str, str]


class ListItemResponse(TypedDict):
    """List item from Trakt API."""

    name: str
    description: str
    privacy: str
    share_link: NotRequired[str]
    type: str
    display_numbers: NotRequired[bool]
    allow_comments: NotRequired[bool]
    sort_by: NotRequired[str]
    sort_how: NotRequired[str]
    created_at: NotRequired[str]
    updated_at: NotRequired[str]
    item_count: int
    comment_count: int
    likes: int
    ids: TraktIdsDict
    user: ListUserResponse
