"""Protocol definitions for type-safe client interfaces."""

from typing import Protocol, runtime_checkable

from config.api import DEFAULT_LIMIT
from models.auth import TraktAuthToken, TraktDeviceCode

from .api_responses import (
    CheckinResponse,
    CommentResponse,
    MovieResponse,
    SearchResult,
    ShowResponse,
    TraktRating,
    TrendingWrapper,
    UserWatchedMovie,
    UserWatchedShow,
)
from .pagination import PaginatedResponse
from .sort import MovieCommentSort, SeasonCommentSort, ShowCommentSort


@runtime_checkable
class AuthClientProtocol(Protocol):
    """Protocol for authentication clients."""

    async def get_device_code(self) -> TraktDeviceCode:
        """Get OAuth device code."""
        ...

    async def get_device_token(self, device_code: str) -> TraktAuthToken:
        """Poll for device token."""
        ...

    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        ...

    def clear_auth(self) -> None:
        """Clear authentication."""
        ...


@runtime_checkable
class ShowsClientProtocol(Protocol):
    """Protocol for show clients."""

    async def get_trending_shows(
        self, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[TrendingWrapper] | PaginatedResponse[TrendingWrapper]:
        """Get trending shows.

        Args:
            limit: Items per page
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all trending shows across all pages
            If page specified: Paginated response with metadata for that page
        """
        ...

    async def get_popular_shows(
        self, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[ShowResponse] | PaginatedResponse[ShowResponse]:
        """Get popular shows.

        Args:
            limit: Items per page
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all popular shows across all pages
            If page specified: Paginated response with metadata for that page
        """
        ...

    async def get_show_summary(
        self, show_id: str, extended: bool = True
    ) -> ShowResponse:
        """Get show details."""
        ...

    async def get_show_ratings(self, show_id: str) -> TraktRating:
        """Get show ratings."""
        ...

    async def get_show_comments(
        self,
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: ShowCommentSort = "newest",
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get show comments."""
        ...


@runtime_checkable
class MoviesClientProtocol(Protocol):
    """Protocol for movie clients."""

    async def get_trending_movies(
        self, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[TrendingWrapper] | PaginatedResponse[TrendingWrapper]:
        """Get trending movies.

        Args:
            limit: Items per page
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all trending movies across all pages
            If page specified: Paginated response with metadata for that page
        """
        ...

    async def get_popular_movies(
        self, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[MovieResponse] | PaginatedResponse[MovieResponse]:
        """Get popular movies.

        Args:
            limit: Items per page
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all popular movies across all pages
            If page specified: Paginated response with metadata for that page
        """
        ...

    async def get_movie_summary(
        self, movie_id: str, extended: bool = True
    ) -> MovieResponse:
        """Get movie details."""
        ...

    async def get_movie_ratings(self, movie_id: str) -> TraktRating:
        """Get movie ratings."""
        ...

    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: MovieCommentSort = "newest",
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get movie comments."""
        ...


@runtime_checkable
class SeasonCommentsClientProtocol(Protocol):
    """Protocol for season comments operations."""

    async def get_season_comments(
        self,
        show_id: str,
        season: int,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: SeasonCommentSort = "newest",
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get season comments."""
        ...


@runtime_checkable
class CheckinClientProtocol(Protocol):
    """Protocol for checkin operations."""

    async def checkin_to_show(
        self,
        episode_season: int,
        episode_number: int,
        show_id: str | None = None,
        show_title: str | None = None,
        show_year: int | None = None,
        message: str = "",
        share_twitter: bool = False,
        share_mastodon: bool = False,
        share_tumblr: bool = False,
    ) -> CheckinResponse:
        """Check in to a show."""
        ...


@runtime_checkable
class SearchClientProtocol(Protocol):
    """Protocol for search operations."""

    async def search_shows(
        self, query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[SearchResult] | PaginatedResponse[SearchResult]:
        """Search for shows.

        Args:
            query: Search query string
            limit: Items per page
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all search results across all pages
            If page specified: Paginated response with metadata for that page
        """
        ...

    async def search_movies(
        self, query: str, limit: int = DEFAULT_LIMIT, page: int | None = None
    ) -> list[SearchResult] | PaginatedResponse[SearchResult]:
        """Search for movies.

        Args:
            query: Search query string
            limit: Items per page
            page: Page number (optional). If None, returns all results via auto-pagination.

        Returns:
            If page is None: List of all search results across all pages
            If page specified: Paginated response with metadata for that page
        """
        ...


@runtime_checkable
class UserClientProtocol(Protocol):
    """Protocol for user operations."""

    async def get_watched_shows(self, limit: int = 0) -> list[UserWatchedShow]:
        """Get user's watched shows."""
        ...

    async def get_watched_movies(self, limit: int = 0) -> list[UserWatchedMovie]:
        """Get user's watched movies."""
        ...
