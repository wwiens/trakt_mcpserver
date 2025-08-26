"""Tests for the client.sync.ratings_client module."""

import os
from unittest.mock import patch

import httpx
import pytest

from client.sync.client import SyncClient
from client.sync.ratings_client import SyncRatingsClient
from models.auth.auth import TraktAuthToken
from models.movies.movie import TraktMovie
from models.shows.show import TraktShow
from models.sync.ratings import (
    SyncRatingsSummary,
    TraktSyncRating,
    TraktSyncRatingItem,
    TraktSyncRatingsRequest,
)
from utils.api.error_types import TraktResourceNotFoundError

# Sample API response data based on USER_RATINGS_DOC.MD
SAMPLE_MOVIE_RATINGS_RESPONSE = [
    {
        "rated_at": "2014-09-01T09:10:11.000Z",
        "rating": 10,
        "type": "movie",
        "movie": {
            "title": "TRON: Legacy",
            "year": 2010,
            "ids": {
                "trakt": "1",
                "slug": "tron-legacy-2010",
                "imdb": "tt1104001",
                "tmdb": "20526",
            },
        },
    },
    {
        "rated_at": "2014-09-01T09:10:11.000Z",
        "rating": 10,
        "type": "movie",
        "movie": {
            "title": "The Dark Knight",
            "year": 2008,
            "ids": {
                "trakt": "6",
                "slug": "the-dark-knight-2008",
                "imdb": "tt0468569",
                "tmdb": "155",
            },
        },
    },
]

SAMPLE_SHOW_RATINGS_RESPONSE = [
    {
        "rated_at": "2014-09-01T09:10:11.000Z",
        "rating": 10,
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

SAMPLE_ADD_RATINGS_RESPONSE = {
    "added": {"movies": 1, "shows": 1, "seasons": 1, "episodes": 2},
    "not_found": {
        "movies": [{"rating": 10, "ids": {"imdb": "tt0000111"}}],
        "shows": [],
        "seasons": [],
        "episodes": [],
    },
}

SAMPLE_REMOVE_RATINGS_RESPONSE: dict[str, dict[str, int | list[dict[str, str]]]] = {
    "removed": {"movies": 2, "shows": 1, "seasons": 0, "episodes": 1},
    "not_found": {"movies": [], "shows": [], "seasons": [], "episodes": []},
}


class TestSyncRatingsClient:
    """Tests for the SyncRatingsClient."""

    @pytest.fixture
    def mock_env(self) -> dict[str, str]:
        """Mock environment variables for testing."""
        return {
            "TRAKT_CLIENT_ID": "test_client_id",
            "TRAKT_CLIENT_SECRET": "test_client_secret",
        }

    @pytest.fixture
    def authenticated_client(self, mock_env: dict[str, str]) -> SyncRatingsClient:
        """Create an authenticated sync ratings client for testing."""
        with patch.dict(os.environ, mock_env):
            client = SyncRatingsClient()
            # Mock authentication status
            client.auth_token = create_mock_auth_token()
            # Mock the is_authenticated method to return True
            client.is_authenticated = lambda: True
            return client

    @pytest.fixture
    def unauthenticated_client(self, mock_env: dict[str, str]) -> SyncRatingsClient:
        """Create an unauthenticated sync ratings client for testing."""
        with patch.dict(os.environ, mock_env):
            client = SyncRatingsClient()
            # Explicitly mock is_authenticated to return False
            client.is_authenticated = lambda: False
            return client

    @pytest.mark.asyncio
    async def test_get_sync_ratings_movies_success(
        self, authenticated_client: SyncRatingsClient
    ) -> None:
        """Test successful retrieval of movie ratings."""
        with patch.object(
            authenticated_client, "_make_typed_list_request"
        ) as mock_request:
            # Mock the response
            mock_ratings = [
                create_movie_rating("TRON: Legacy", 2010, "1", 10),
                create_movie_rating("The Dark Knight", 2008, "6", 10),
            ]
            mock_request.return_value = mock_ratings

            result = await authenticated_client.get_sync_ratings("movies")

            assert len(result) == 2
            assert result[0].type == "movie"
            assert result[0].movie is not None
            assert result[0].movie.title == "TRON: Legacy"
            assert result[1].movie is not None
            assert result[1].movie.title == "The Dark Knight"

            # Verify correct endpoint was called
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert "/sync/ratings/movies" in args[0]
            assert kwargs["response_type"] == TraktSyncRating

    @pytest.mark.asyncio
    async def test_get_sync_ratings_shows_with_rating_filter(
        self, authenticated_client: SyncRatingsClient
    ) -> None:
        """Test retrieval of show ratings with specific rating filter."""
        with patch.object(
            authenticated_client, "_make_typed_list_request"
        ) as mock_request:
            mock_ratings = [create_show_rating("Breaking Bad", 2008, "1", 10)]
            mock_request.return_value = mock_ratings

            result = await authenticated_client.get_sync_ratings("shows", rating=10)

            assert len(result) == 1
            assert result[0].type == "show"
            assert result[0].rating == 10
            assert result[0].show is not None
            assert result[0].show.title == "Breaking Bad"

            # Verify correct endpoint was called with rating filter
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            assert "/sync/ratings/shows/10" in args[0]

    @pytest.mark.asyncio
    async def test_get_sync_ratings_unauthenticated(
        self, unauthenticated_client: SyncRatingsClient
    ) -> None:
        """Test that unauthenticated requests raise ValueError."""
        with pytest.raises(
            ValueError,
            match="You must be authenticated to access your personal ratings",
        ):
            await unauthenticated_client.get_sync_ratings("movies")

    @pytest.mark.asyncio
    async def test_add_sync_ratings_success(
        self, authenticated_client: SyncRatingsClient
    ) -> None:
        """Test successful addition of ratings."""
        # Prepare request data
        movies = [
            TraktSyncRatingItem(
                rating=9, title="Inception", year=2010, ids={"imdb": "tt1375666"}
            )
        ]
        request = TraktSyncRatingsRequest(movies=movies)

        with patch.object(authenticated_client, "_post_typed_request") as mock_request:
            # Mock the response with proper Pydantic object
            from models.sync.ratings import SyncRatingsNotFound, SyncRatingsSummaryCount

            mock_summary = SyncRatingsSummary(
                added=SyncRatingsSummaryCount(movies=1, shows=1, seasons=1, episodes=2),
                not_found=SyncRatingsNotFound(
                    movies=[TraktSyncRatingItem(rating=10, ids={"imdb": "tt0000111"})],
                    shows=[],
                    seasons=[],
                    episodes=[],
                ),
            )
            mock_request.return_value = mock_summary

            result = await authenticated_client.add_sync_ratings(request)

            assert result.added is not None
            assert result.added.movies == 1
            assert result.added.shows == 1
            assert len(result.not_found.movies) == 1
            assert result.not_found.movies[0].rating == 10

            # Verify correct endpoint and data were used
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "/sync/ratings"
            assert kwargs["response_type"] == SyncRatingsSummary
            # Verify request data structure
            request_data = args[1]
            assert "movies" in request_data
            assert len(request_data["movies"]) == 1

    @pytest.mark.asyncio
    async def test_add_sync_ratings_unauthenticated(
        self, unauthenticated_client: SyncRatingsClient
    ) -> None:
        """Test that unauthenticated add requests raise ValueError."""
        request = TraktSyncRatingsRequest()

        with pytest.raises(
            ValueError, match="You must be authenticated to add personal ratings"
        ):
            await unauthenticated_client.add_sync_ratings(request)

    @pytest.mark.asyncio
    async def test_remove_sync_ratings_success(
        self, authenticated_client: SyncRatingsClient
    ) -> None:
        """Test successful removal of ratings."""
        # Prepare request data (no ratings needed for removal)
        movies = [
            TraktSyncRatingItem(ids={"imdb": "tt1375666"}, title="Inception", year=2010)
        ]
        request = TraktSyncRatingsRequest(movies=movies)

        with patch.object(authenticated_client, "_make_request") as mock_request:
            # Mock the response
            mock_request.return_value = SAMPLE_REMOVE_RATINGS_RESPONSE

            result = await authenticated_client.remove_sync_ratings(request)

            assert result.removed is not None
            assert result.removed.movies == 2
            assert result.removed.shows == 1
            assert result.removed.episodes == 1
            assert len(result.not_found.movies) == 0

            # Verify DELETE method was used
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "DELETE"
            assert args[1] == "/sync/ratings"
            assert "data" in kwargs

    @pytest.mark.asyncio
    async def test_remove_sync_ratings_unauthenticated(
        self, unauthenticated_client: SyncRatingsClient
    ) -> None:
        """Test that unauthenticated remove requests raise ValueError."""
        request = TraktSyncRatingsRequest()

        with pytest.raises(
            ValueError, match="You must be authenticated to remove personal ratings"
        ):
            await unauthenticated_client.remove_sync_ratings(request)

    @pytest.mark.asyncio
    async def test_get_sync_ratings_error_handling(
        self, authenticated_client: SyncRatingsClient
    ) -> None:
        """Test error handling in get_sync_ratings."""
        with patch.object(
            authenticated_client, "_make_typed_list_request"
        ) as mock_request:
            # Mock an HTTP error
            mock_request.side_effect = httpx.HTTPStatusError(
                "Not found",
                request=httpx.Request("GET", "http://test.com"),
                response=httpx.Response(404),
            )

            # Error handler converts HTTPStatusError to TraktResourceNotFoundError
            with pytest.raises(TraktResourceNotFoundError):
                await authenticated_client.get_sync_ratings("movies")

    @pytest.mark.asyncio
    async def test_add_sync_ratings_http_error(
        self, authenticated_client: SyncRatingsClient
    ) -> None:
        """Test HTTP error in add_sync_ratings."""
        with patch.object(authenticated_client, "_post_typed_request") as mock_request:
            # Mock an HTTP error response
            mock_request.side_effect = Exception("HTTP error")

            request = TraktSyncRatingsRequest(movies=[])

            with pytest.raises(Exception, match="HTTP error"):
                await authenticated_client.add_sync_ratings(request)

    @pytest.mark.asyncio
    async def test_endpoint_url_construction(
        self, authenticated_client: SyncRatingsClient
    ) -> None:
        """Test correct endpoint URL construction."""
        with patch.object(
            authenticated_client, "_make_typed_list_request"
        ) as mock_request:
            mock_request.return_value = []

            # Test different endpoint constructions
            await authenticated_client.get_sync_ratings("movies")
            first_call = mock_request.call_args_list[0]
            assert "/sync/ratings/movies" in first_call[0][0]

            await authenticated_client.get_sync_ratings("shows", rating=8)
            second_call = mock_request.call_args_list[1]
            assert "/sync/ratings/shows/8" in second_call[0][0]

            await authenticated_client.get_sync_ratings("episodes", rating=5)
            third_call = mock_request.call_args_list[2]
            assert "/sync/ratings/episodes/5" in third_call[0][0]


class TestSyncClient:
    """Tests for the main SyncClient."""

    @pytest.fixture
    def mock_env(self) -> dict[str, str]:
        """Mock environment variables for testing."""
        return {
            "TRAKT_CLIENT_ID": "test_client_id",
            "TRAKT_CLIENT_SECRET": "test_client_secret",
        }

    @pytest.mark.asyncio
    async def test_sync_client_inheritance(self, mock_env: dict[str, str]) -> None:
        """Test that SyncClient properly inherits SyncRatingsClient methods."""
        with patch.dict(os.environ, mock_env):
            client = SyncClient()

            # Verify it has the ratings methods
            assert hasattr(client, "get_sync_ratings")
            assert hasattr(client, "add_sync_ratings")
            assert hasattr(client, "remove_sync_ratings")

            # Verify it inherits authentication
            assert hasattr(client, "is_authenticated")
            assert hasattr(client, "auth_token")

    @pytest.mark.asyncio
    async def test_sync_client_ratings_functionality(
        self, mock_env: dict[str, str]
    ) -> None:
        """Test that SyncClient can perform rating operations."""
        with patch.dict(os.environ, mock_env):
            client = SyncClient()
            client.auth_token = create_mock_auth_token()
            # Mock the is_authenticated method to return True
            client.is_authenticated = lambda: True

            with patch.object(client, "_make_typed_list_request") as mock_request:
                mock_request.return_value = []

                result = await client.get_sync_ratings("movies")
                assert result == []

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


def create_movie_rating(
    title: str, year: int, trakt_id: str, rating: int
) -> TraktSyncRating:
    """Create a TraktSyncRating for a movie."""
    movie = TraktMovie(
        title=title,
        year=year,
        ids={"trakt": trakt_id, "slug": f"{title.lower().replace(' ', '-')}-{year}"},
    )
    return TraktSyncRating(
        rated_at="2014-09-01T09:10:11.000Z", rating=rating, type="movie", movie=movie
    )


def create_show_rating(
    title: str, year: int, trakt_id: str, rating: int
) -> TraktSyncRating:
    """Create a TraktSyncRating for a show."""
    show = TraktShow(
        title=title,
        year=year,
        ids={"trakt": trakt_id, "slug": title.lower().replace(" ", "-")},
    )
    return TraktSyncRating(
        rated_at="2014-09-01T09:10:11.000Z", rating=rating, type="show", show=show
    )
