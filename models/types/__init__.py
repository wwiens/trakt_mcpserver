"""Type definitions for Trakt API."""

from .api_responses import (
    CheckinResponse,
    CommentResponse,
    DeviceCodeResponse,
    EpisodeResponse,
    FavoritedMovieWrapper,
    FavoritedShowWrapper,
    MovieResponse,
    PlayedMovieWrapper,
    PlayedShowWrapper,
    SearchResult,
    SeasonResponse,
    ShowResponse,
    StatsResponse,
    TokenResponse,
    TraktIds,
    TraktRating,
    TrendingWrapper,
    UserResponse,
    UserWatchedEpisode,
    UserWatchedMovie,
    UserWatchedSeason,
    UserWatchedShow,
    WatchedMovieWrapper,
    WatchedShowWrapper,
)
from .common import (
    ErrorResponse,
    PaginatedResponse,
    T,
    TraktHeaders,
    TRequest,
    TResponse,
)
from .pagination import (
    PaginationMetadata,
    PaginationParams,
)
from .protocols import (
    AuthClientProtocol,
    CheckinClientProtocol,
    MoviesClientProtocol,
    SearchClientProtocol,
    ShowsClientProtocol,
    UserClientProtocol,
)
from .sort import (
    EpisodeCommentSort,
    MovieCommentSort,
    SeasonCommentSort,
    ShowCommentSort,
)

__all__ = [
    # Protocol Types
    "AuthClientProtocol",
    "CheckinClientProtocol",
    "CheckinResponse",
    "CommentResponse",
    "DeviceCodeResponse",
    "EpisodeCommentSort",
    "EpisodeResponse",
    "ErrorResponse",
    "FavoritedMovieWrapper",
    "FavoritedShowWrapper",
    "MovieCommentSort",
    "MovieResponse",
    "MoviesClientProtocol",
    # Common Types
    "PaginatedResponse",
    # Pagination Types
    "PaginationMetadata",
    "PaginationParams",
    "PlayedMovieWrapper",
    "PlayedShowWrapper",
    "SearchClientProtocol",
    "SearchResult",
    "SeasonCommentSort",
    "SeasonResponse",
    "ShowCommentSort",
    "ShowResponse",
    "ShowsClientProtocol",
    # Sort Types
    "StatsResponse",
    "T",
    "TRequest",
    "TResponse",
    "TokenResponse",
    "TraktHeaders",
    # API Response Types
    "TraktIds",
    "TraktRating",
    "TrendingWrapper",
    "UserClientProtocol",
    "UserResponse",
    "UserWatchedEpisode",
    "UserWatchedMovie",
    "UserWatchedSeason",
    "UserWatchedShow",
    "WatchedMovieWrapper",
    "WatchedShowWrapper",
]
