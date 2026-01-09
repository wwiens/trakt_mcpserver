"""Tests for the client.sync.watchlist_client module."""

from datetime import datetime
from unittest.mock import patch

import httpx
import pytest

from client.sync.client import SyncClient
from client.sync.watchlist_client import SyncWatchlistClient
from models.auth.auth import TraktAuthToken
from models.movies.movie import TraktMovie
from models.shows.episode import TraktEpisode
from models.shows.show import TraktShow
from models.sync.watchlist import (
    SyncWatchlistNotFound,
    SyncWatchlistSummary,
    SyncWatchlistSummaryCount,
    TraktSyncWatchlistItem,
    TraktSyncWatchlistRequest,
    TraktWatchlistItem,
)
from models.types.pagination import (
    PaginatedResponse,
    PaginationMetadata,
    PaginationParams,
)
from utils.api.error_types import TraktResourceNotFoundError

# Sample API response data for watchlist items
SAMPLE_MOVIE_WATCHLIST_RESPONSE = [
    {
        "rank": 1,
        "id": 12345,
        "listed_at": "2024-01-15T10:30:00.000Z",
        "notes": "Must watch ASAP!",
        "type": "movie",
        "movie": {
            "title": "Inception",
            "year": 2010,
            "ids": {
                "trakt": "1",
                "slug": "inception-2010",
                "imdb": "tt1375666",
                "tmdb": "27205",
            },
        },
    },
    {
        "rank": 2,
        "id": 12346,
        "listed_at": "2024-01-16T14:20:00.000Z",
        "notes": None,
        "type": "movie",
        "movie": {
            "title": "The Matrix",
            "year": 1999,
            "ids": {
                "trakt": "6",
                "slug": "the-matrix-1999",
                "imdb": "tt0133093",
                "tmdb": "603",
            },
        },
    },
]

SAMPLE_SHOW_WATCHLIST_RESPONSE = [
    {
        "rank": 1,
        "id": 54321,
        "listed_at": "2024-01-10T09:00:00.000Z",
        "notes": "VIP exclusive show",
        "type": "show",
        "show": {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {
                "trakt": "1",
                "slug": "breaking-bad",
                "tvdb": "81189",
                "imdb": "tt0903747",
                "tmdb": "1396",
            },
        },
    }
]

SAMPLE_ADD_WATCHLIST_RESPONSE = {
    "added": {"movies": 2, "shows": 1, "seasons": 0, "episodes": 0},
    "existing": {"movies": 1, "shows": 0, "seasons": 0, "episodes": 0},
    "not_found": {
        "movies": [
            {"title": "Unknown Movie", "year": 2099, "ids": {"imdb": "tt9999999"}}
        ],
        "shows": [],
        "seasons": [],
        "episodes": [],
    },
}

SAMPLE_REMOVE_WATCHLIST_RESPONSE: dict[str, dict[str, int | list[dict[str, str]]]] = {
    "removed": {"movies": 2, "shows": 1, "seasons": 0, "episodes": 1},
    "not_found": {"movies": [], "shows": [], "seasons": [], "episodes": []},
}


class TestSyncWatchlistClient:
    """Tests for the SyncWatchlistClient."""

    @pytest.fixture
    def mock_env(self) -> dict[str, str]:
        """Mock environment variables for testing."""
        return {
            "TRAKT_CLIENT_ID": "test_client_id",
            "TRAKT_CLIENT_SECRET": "test_client_secret",
        }

    @pytest.fixture
    def authenticated_client(
        self, mock_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> SyncWatchlistClient:
        """Create an authenticated sync watchlist client for testing."""
        for key, value in mock_env.items():
            monkeypatch.setenv(key, value)

        client = SyncWatchlistClient()
        # Mock authentication status
        client.auth_token = create_mock_auth_token()
        # Mock the is_authenticated method to return True
        client.is_authenticated = lambda: True
        return client

    @pytest.fixture
    def unauthenticated_client(
        self, mock_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> SyncWatchlistClient:
        """Create an unauthenticated sync watchlist client for testing."""
        for key, value in mock_env.items():
            monkeypatch.setenv(key, value)

        client = SyncWatchlistClient()
        # Explicitly mock is_authenticated to return False
        client.is_authenticated = lambda: False
        return client

    @pytest.mark.asyncio
    async def test_get_sync_watchlist_movies_success(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test successful retrieval of movie watchlist."""
        with patch.object(
            authenticated_client, "_make_paginated_request"
        ) as mock_request:
            # Mock the paginated response
            mock_items = [
                create_movie_watchlist_item("Inception", 2010, "1", 1, "Must watch!"),
                create_movie_watchlist_item("The Matrix", 1999, "6", 2, None),
            ]
            mock_pagination = PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=2
            )
            mock_paginated_response = PaginatedResponse[TraktWatchlistItem](
                data=mock_items, pagination=mock_pagination
            )
            mock_request.return_value = mock_paginated_response

            result = await authenticated_client.get_sync_watchlist("movies")

            assert len(result.data) == 2
            assert result.data[0].type == "movie"
            assert result.data[0].movie is not None
            assert result.data[0].movie.title == "Inception"
            assert result.data[0].notes == "Must watch!"
            assert result.data[1].movie is not None
            assert result.data[1].movie.title == "The Matrix"
            assert result.data[1].notes is None

            # Verify correct endpoint was called
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert "/sync/watchlist/movies" in args[0]
            assert kwargs["response_type"] == TraktWatchlistItem

    @pytest.mark.asyncio
    async def test_get_sync_watchlist_shows_with_sorting(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test retrieval of show watchlist with sorting parameters."""
        with patch.object(
            authenticated_client, "_make_paginated_request"
        ) as mock_request:
            mock_items = [
                create_show_watchlist_item("Breaking Bad", 2008, "1", 1, "VIP show")
            ]
            mock_pagination = PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=1
            )
            mock_paginated_response = PaginatedResponse[TraktWatchlistItem](
                data=mock_items, pagination=mock_pagination
            )
            mock_request.return_value = mock_paginated_response

            result = await authenticated_client.get_sync_watchlist(
                "shows", sort_by="added", sort_how="desc"
            )

            assert len(result.data) == 1
            assert result.data[0].type == "show"
            assert result.data[0].show is not None
            assert result.data[0].show.title == "Breaking Bad"

            # Verify correct endpoint was called with sorting
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            assert "/sync/watchlist/shows/added/desc" in args[0]

    @pytest.mark.asyncio
    async def test_get_sync_watchlist_all_types(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test retrieval of all watchlist types."""
        with patch.object(
            authenticated_client, "_make_paginated_request"
        ) as mock_request:
            mock_items = [
                create_movie_watchlist_item("Inception", 2010, "1", 1, None),
                create_show_watchlist_item("Breaking Bad", 2008, "2", 2, None),
            ]
            mock_pagination = PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=2
            )
            mock_paginated_response = PaginatedResponse[TraktWatchlistItem](
                data=mock_items, pagination=mock_pagination
            )
            mock_request.return_value = mock_paginated_response

            result = await authenticated_client.get_sync_watchlist("all")

            assert len(result.data) == 2
            assert result.data[0].type == "movie"
            assert result.data[1].type == "show"

            # Verify correct endpoint was called (should use simple endpoint)
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            assert args[0] == "/sync/watchlist"

    @pytest.mark.asyncio
    async def test_get_sync_watchlist_with_pagination(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test retrieval of watchlist with pagination."""
        with patch.object(
            authenticated_client, "_make_paginated_request"
        ) as mock_request:
            mock_items = [create_movie_watchlist_item("Movie 1", 2020, "1", 1, None)]
            mock_pagination = PaginationMetadata(
                current_page=2, items_per_page=5, total_pages=3, total_items=15
            )
            mock_paginated_response = PaginatedResponse[TraktWatchlistItem](
                data=mock_items, pagination=mock_pagination
            )
            mock_request.return_value = mock_paginated_response

            pagination_params = PaginationParams(page=2, limit=5)
            result = await authenticated_client.get_sync_watchlist(
                "movies", pagination=pagination_params
            )

            assert result.pagination.current_page == 2
            assert result.pagination.total_pages == 3
            assert result.pagination.has_previous_page
            assert result.pagination.has_next_page

            # Verify pagination params were passed
            mock_request.assert_called_once()
            _, kwargs = mock_request.call_args
            assert "params" in kwargs
            assert kwargs["params"]["page"] == 2
            assert kwargs["params"]["limit"] == 5

    @pytest.mark.asyncio
    async def test_get_sync_watchlist_unauthenticated(
        self, unauthenticated_client: SyncWatchlistClient
    ) -> None:
        """Test that unauthenticated requests raise ValueError."""
        with pytest.raises(
            ValueError,
            match="You must be authenticated to access your personal watchlist",
        ):
            await unauthenticated_client.get_sync_watchlist("movies")

    @pytest.mark.asyncio
    async def test_add_sync_watchlist_success(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test successful addition of items to watchlist."""
        # Prepare request data
        movies = [
            TraktSyncWatchlistItem(
                title="Inception",
                year=2010,
                ids={"imdb": "tt1375666"},
                notes="Must watch!",
            )
        ]
        request = TraktSyncWatchlistRequest(movies=movies)

        with patch.object(authenticated_client, "_post_typed_request") as mock_request:
            # Mock the response with proper Pydantic object
            mock_summary = SyncWatchlistSummary(
                added=SyncWatchlistSummaryCount(
                    movies=2, shows=1, seasons=0, episodes=0
                ),
                existing=SyncWatchlistSummaryCount(
                    movies=1, shows=0, seasons=0, episodes=0
                ),
                not_found=SyncWatchlistNotFound(
                    movies=[
                        TraktSyncWatchlistItem(
                            title="Unknown Movie",
                            year=2099,
                            ids={"imdb": "tt9999999"},
                        )
                    ],
                    shows=[],
                    seasons=[],
                    episodes=[],
                ),
            )
            mock_request.return_value = mock_summary

            result = await authenticated_client.add_sync_watchlist(request)

            assert result.added is not None
            assert result.added.movies == 2
            assert result.added.shows == 1
            assert result.existing is not None
            assert result.existing.movies == 1
            assert len(result.not_found.movies) == 1
            assert result.not_found.movies[0].title == "Unknown Movie"

            # Verify correct endpoint and data were used
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "/sync/watchlist"
            assert kwargs["response_type"] == SyncWatchlistSummary
            # Verify request data structure
            request_data = args[1]
            assert "movies" in request_data
            assert len(request_data["movies"]) == 1

    @pytest.mark.asyncio
    async def test_add_sync_watchlist_with_notes(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test adding watchlist items with notes (VIP feature)."""
        movies = [
            TraktSyncWatchlistItem(
                title="Interstellar",
                year=2014,
                ids={"imdb": "tt0816692"},
                notes="Watch on IMAX" * 10,  # VIP notes up to 500 chars
            )
        ]
        request = TraktSyncWatchlistRequest(movies=movies)

        with patch.object(authenticated_client, "_post_typed_request") as mock_request:
            mock_summary = SyncWatchlistSummary(
                added=SyncWatchlistSummaryCount(movies=1),
                not_found=SyncWatchlistNotFound(
                    movies=[], shows=[], seasons=[], episodes=[]
                ),
            )
            mock_request.return_value = mock_summary

            result = await authenticated_client.add_sync_watchlist(request)

            assert result.added is not None
            assert result.added.movies == 1

            # Verify notes were included in request
            args, _ = mock_request.call_args
            request_data = args[1]
            assert request_data["movies"][0]["notes"] == "Watch on IMAX" * 10

    @pytest.mark.asyncio
    async def test_add_sync_watchlist_unauthenticated(
        self, unauthenticated_client: SyncWatchlistClient
    ) -> None:
        """Test that unauthenticated add requests raise ValueError."""
        request = TraktSyncWatchlistRequest(
            movies=[TraktSyncWatchlistItem(ids={"trakt": 123})]
        )

        with pytest.raises(
            ValueError, match="You must be authenticated to add items to your watchlist"
        ):
            await unauthenticated_client.add_sync_watchlist(request)

    @pytest.mark.asyncio
    async def test_remove_sync_watchlist_success(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test successful removal of items from watchlist."""
        # Prepare request data (no notes needed for removal)
        movies = [
            TraktSyncWatchlistItem(
                ids={"imdb": "tt1375666"}, title="Inception", year=2010
            )
        ]
        request = TraktSyncWatchlistRequest(movies=movies)

        with patch.object(authenticated_client, "_post_typed_request") as mock_request:
            # Mock the response with proper Pydantic object
            mock_summary = SyncWatchlistSummary(
                deleted=SyncWatchlistSummaryCount(
                    movies=2, shows=1, seasons=0, episodes=1
                ),
                not_found=SyncWatchlistNotFound(
                    movies=[], shows=[], seasons=[], episodes=[]
                ),
            )
            mock_request.return_value = mock_summary

            result = await authenticated_client.remove_sync_watchlist(request)

            assert result.deleted is not None
            assert result.deleted.movies == 2
            assert result.deleted.shows == 1
            assert result.deleted.episodes == 1
            assert len(result.not_found.movies) == 0

            # Verify correct endpoint and data were used
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "/sync/watchlist/remove"
            assert kwargs["response_type"] == SyncWatchlistSummary
            # Verify request data structure
            request_data = args[1]
            assert "movies" in request_data
            assert len(request_data["movies"]) == 1

    @pytest.mark.asyncio
    async def test_remove_sync_watchlist_unauthenticated(
        self, unauthenticated_client: SyncWatchlistClient
    ) -> None:
        """Test that unauthenticated remove requests raise ValueError."""
        request = TraktSyncWatchlistRequest(
            movies=[TraktSyncWatchlistItem(ids={"trakt": 123})]
        )

        with pytest.raises(
            ValueError,
            match="You must be authenticated to remove items from your watchlist",
        ):
            await unauthenticated_client.remove_sync_watchlist(request)

    @pytest.mark.asyncio
    async def test_get_sync_watchlist_error_handling(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test error handling in get_sync_watchlist."""
        with patch.object(
            authenticated_client, "_make_paginated_request"
        ) as mock_request:
            # Mock an HTTP error
            mock_request.side_effect = httpx.HTTPStatusError(
                "Not found",
                request=httpx.Request("GET", "http://test.com"),
                response=httpx.Response(404),
            )

            # Error handler converts HTTPStatusError to TraktResourceNotFoundError
            with pytest.raises(TraktResourceNotFoundError):
                await authenticated_client.get_sync_watchlist("movies")

    @pytest.mark.asyncio
    async def test_add_sync_watchlist_http_error(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test HTTP error in add_sync_watchlist."""
        with patch.object(authenticated_client, "_post_typed_request") as mock_request:
            # Mock an HTTP error response
            mock_request.side_effect = Exception("HTTP error")

            request = TraktSyncWatchlistRequest(
                movies=[TraktSyncWatchlistItem(ids={"trakt": 123})]
            )

            with pytest.raises(Exception, match="HTTP error"):
                await authenticated_client.add_sync_watchlist(request)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "watchlist_type,sort_by,sort_how,expected_endpoint",
        [
            ("all", "rank", "asc", "/sync/watchlist"),
            ("movies", "rank", "asc", "/sync/watchlist/movies"),
            ("shows", "added", "desc", "/sync/watchlist/shows/added/desc"),
            ("episodes", "title", "asc", "/sync/watchlist/episodes/title/asc"),
        ],
    )
    async def test_endpoint_url_construction(
        self,
        authenticated_client: SyncWatchlistClient,
        watchlist_type: str,
        sort_by: str,
        sort_how: str,
        expected_endpoint: str,
    ) -> None:
        """Test correct endpoint URL construction."""
        with patch.object(
            authenticated_client, "_make_paginated_request"
        ) as mock_request:
            # Mock empty paginated response
            mock_pagination = PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=0
            )
            empty_paginated_response = PaginatedResponse[TraktWatchlistItem](
                data=[], pagination=mock_pagination
            )
            mock_request.return_value = empty_paginated_response

            # Test endpoint construction
            await authenticated_client.get_sync_watchlist(
                watchlist_type,
                sort_by=sort_by,
                sort_how=sort_how,  # type: ignore
            )
            assert expected_endpoint in mock_request.call_args[0][0]

    @pytest.mark.asyncio
    async def test_get_sync_watchlist_pagination_metadata(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test pagination metadata properties."""
        with patch.object(
            authenticated_client, "_make_paginated_request"
        ) as mock_request:
            # Test case with multiple pages
            mock_items = [
                create_movie_watchlist_item("Test Movie", 2020, "999", 1, None)
            ]
            mock_pagination = PaginationMetadata(
                current_page=2, items_per_page=5, total_pages=4, total_items=18
            )
            mock_paginated_response = PaginatedResponse[TraktWatchlistItem](
                data=mock_items, pagination=mock_pagination
            )
            mock_request.return_value = mock_paginated_response

            result = await authenticated_client.get_sync_watchlist(
                "movies", pagination=PaginationParams(page=2, limit=5)
            )

            # Test pagination properties
            pagination = result.pagination
            assert pagination.has_previous_page
            assert pagination.has_next_page
            assert pagination.previous_page() == 1
            assert pagination.next_page() == 3
            assert not result.is_empty
            assert not result.is_single_page

            # Test page info summary
            summary = result.page_info_summary()
            assert "Page 2 of 4" in summary
            assert "18" in summary  # total items

    @pytest.mark.asyncio
    async def test_get_sync_watchlist_empty_result(
        self, authenticated_client: SyncWatchlistClient
    ) -> None:
        """Test request with empty results."""
        with patch.object(
            authenticated_client, "_make_paginated_request"
        ) as mock_request:
            mock_pagination = PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=0
            )
            mock_paginated_response = PaginatedResponse[TraktWatchlistItem](
                data=[], pagination=mock_pagination
            )
            mock_request.return_value = mock_paginated_response

            result = await authenticated_client.get_sync_watchlist("movies")

            assert len(result.data) == 0
            assert result.is_empty
            assert result.is_single_page
            assert result.pagination.total_items == 0


class TestSyncWatchlistSecurity:
    """Security tests for watchlist functionality."""

    def test_sort_by_path_traversal_prevention(self) -> None:
        """Test that path traversal attempts in sort_by are prevented."""
        from pydantic import ValidationError

        from server.sync.tools import UserWatchlistParams

        # Test various path traversal attempts
        invalid_sort_by_values = [
            "../../users/settings",
            "../../../admin",
            "rank/../../../secrets",
            "rank/../../etc/passwd",
            "..",
            ".",
            "/etc/passwd",
            "\\windows\\system32",
        ]

        for invalid_value in invalid_sort_by_values:
            with pytest.raises(ValidationError) as exc_info:
                UserWatchlistParams(sort_by=invalid_value)  # type: ignore[arg-type]

            # Verify the error mentions the invalid value
            error = exc_info.value
            assert "sort_by" in str(error).lower()

    def test_valid_sort_by_values(self) -> None:
        """Test that valid sort_by values are accepted."""
        from typing import Literal

        from server.sync.tools import UserWatchlistParams

        valid_sort_by_values: list[
            Literal[
                "rank",
                "added",
                "title",
                "released",
                "runtime",
                "popularity",
                "percentage",
                "votes",
            ]
        ] = [
            "rank",
            "added",
            "title",
            "released",
            "runtime",
            "popularity",
            "percentage",
            "votes",
        ]

        for valid_value in valid_sort_by_values:
            # Should not raise any exception
            params = UserWatchlistParams(sort_by=valid_value)
            assert params.sort_by == valid_value


class TestSyncClient:
    """Tests for the main SyncClient with watchlist support."""

    @pytest.fixture
    def mock_env(self) -> dict[str, str]:
        """Mock environment variables for testing."""
        return {
            "TRAKT_CLIENT_ID": "test_client_id",
            "TRAKT_CLIENT_SECRET": "test_client_secret",
        }

    @pytest.mark.asyncio
    async def test_sync_client_inheritance(
        self, mock_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that SyncClient properly inherits watchlist methods."""
        for key, value in mock_env.items():
            monkeypatch.setenv(key, value)

        client = SyncClient()

        # Verify it has the watchlist methods
        assert hasattr(client, "get_sync_watchlist")
        assert hasattr(client, "add_sync_watchlist")
        assert hasattr(client, "remove_sync_watchlist")

        # Verify it has the ratings methods
        assert hasattr(client, "get_sync_ratings")
        assert hasattr(client, "add_sync_ratings")
        assert hasattr(client, "remove_sync_ratings")

        # Verify it inherits authentication
        assert hasattr(client, "is_authenticated")
        assert hasattr(client, "auth_token")

    @pytest.mark.asyncio
    async def test_sync_client_watchlist_functionality(
        self, mock_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that SyncClient can perform watchlist operations."""
        for key, value in mock_env.items():
            monkeypatch.setenv(key, value)

        client = SyncClient()
        client.auth_token = create_mock_auth_token()
        # Mock the is_authenticated method to return True
        client.is_authenticated = lambda: True

        with patch.object(client, "_make_paginated_request") as mock_request:
            # Mock empty paginated response
            mock_pagination = PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=0
            )
            empty_paginated_response = PaginatedResponse[TraktWatchlistItem](
                data=[], pagination=mock_pagination
            )
            mock_request.return_value = empty_paginated_response

            result = await client.get_sync_watchlist("movies")
            assert result.data == []

            mock_request.assert_called_once()


def create_mock_auth_token() -> TraktAuthToken:
    """Create a mock authentication token for testing."""
    return TraktAuthToken(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        created_at=1234567890,
        expires_in=7200,
        scope="public",
        token_type="bearer",
    )


def create_movie_watchlist_item(
    title: str, year: int, trakt_id: str, rank: int, notes: str | None
) -> TraktWatchlistItem:
    """Create a TraktWatchlistItem for a movie."""
    movie = TraktMovie(
        title=title,
        year=year,
        ids={"trakt": trakt_id, "slug": f"{title.lower().replace(' ', '-')}-{year}"},
    )
    return TraktWatchlistItem(
        rank=rank,
        id=int(trakt_id) * 1000,  # Mock ID
        listed_at=datetime.fromisoformat("2024-01-15T10:30:00.000+00:00"),
        notes=notes,
        type="movie",
        movie=movie,
    )


def create_show_watchlist_item(
    title: str, year: int, trakt_id: str, rank: int, notes: str | None
) -> TraktWatchlistItem:
    """Create a TraktWatchlistItem for a show."""
    show = TraktShow(
        title=title,
        year=year,
        ids={"trakt": trakt_id, "slug": title.lower().replace(" ", "-")},
    )
    return TraktWatchlistItem(
        rank=rank,
        id=int(trakt_id) * 1000,  # Mock ID
        listed_at=datetime.fromisoformat("2024-01-10T09:00:00.000+00:00"),
        notes=notes,
        type="show",
        show=show,
    )


def create_episode_watchlist_item(
    show_title: str,
    show_year: int,
    trakt_id: str,
    season_number: int,
    episode_number: int,
    rank: int,
    notes: str | None,
) -> TraktWatchlistItem:
    """Create a TraktWatchlistItem for an episode."""
    show = TraktShow(
        title=show_title,
        year=show_year,
        ids={"trakt": trakt_id, "slug": show_title.lower().replace(" ", "-")},
    )
    episode = TraktEpisode(
        season=season_number,
        number=episode_number,
        title=f"Episode {episode_number}",
        ids={"trakt": f"{trakt_id}_{season_number}_{episode_number}"},
    )
    return TraktWatchlistItem(
        rank=rank,
        id=int(trakt_id) * 1000 + season_number * 100 + episode_number,
        listed_at=datetime.fromisoformat("2024-01-20T12:00:00.000+00:00"),
        notes=notes,
        type="episode",
        show=show,
        episode=episode,
    )
