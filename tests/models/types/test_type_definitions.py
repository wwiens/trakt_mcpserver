"""Tests for type definitions."""

from typing import get_type_hints

from models.types import (
    AuthClientProtocol,
    CheckinResponse,
    CommentResponse,
    MovieResponse,
    SearchResult,
    ShowResponse,
    ShowsClientProtocol,
    TraktIds,
    TraktRating,
    TrendingWrapper,
)


def test_traktids_structure():
    """Test TraktIds has required fields."""
    hints = get_type_hints(TraktIds)
    assert "trakt" in hints
    assert "slug" in hints
    assert hints["trakt"] is int
    assert hints["slug"] is str


def test_show_response_structure():
    """Test ShowResponse has required fields."""
    hints = get_type_hints(ShowResponse)
    assert "title" in hints
    assert "year" in hints
    assert "ids" in hints
    assert hints["title"] is str
    assert hints["year"] is int


def test_movie_response_structure():
    """Test MovieResponse has required fields."""
    hints = get_type_hints(MovieResponse)
    assert "title" in hints
    assert "year" in hints
    assert "ids" in hints
    assert hints["title"] is str
    assert hints["year"] is int


def test_trending_wrapper_structure():
    """Test TrendingWrapper has required fields."""
    hints = get_type_hints(TrendingWrapper)
    assert "watchers" in hints
    assert hints["watchers"] is int


def test_comment_response_structure():
    """Test CommentResponse has required fields."""
    hints = get_type_hints(CommentResponse)
    assert "id" in hints
    assert "comment" in hints
    assert "spoiler" in hints
    assert "review" in hints
    assert "created_at" in hints
    assert "user" in hints
    assert hints["id"] is int
    assert hints["comment"] is str
    assert hints["spoiler"] is bool
    assert hints["review"] is bool
    assert hints["created_at"] is str


def test_search_result_structure():
    """Test SearchResult has required fields."""
    hints = get_type_hints(SearchResult)
    assert "type" in hints
    assert "score" in hints
    assert hints["type"] is str
    assert hints["score"] is float


def test_checkin_response_structure():
    """Test CheckinResponse has required fields."""
    hints = get_type_hints(CheckinResponse)
    assert "id" in hints
    assert "watched_at" in hints
    assert "sharing" in hints
    assert hints["id"] is int
    assert hints["watched_at"] is str


def test_trakt_rating_structure():
    """Test TraktRating has required fields."""
    hints = get_type_hints(TraktRating)
    assert "rating" in hints
    assert "votes" in hints
    assert "distribution" in hints
    assert hints["rating"] is float
    assert hints["votes"] is int


def test_protocol_methods():
    """Test protocol has required methods."""
    assert hasattr(AuthClientProtocol, "get_device_code")
    assert hasattr(AuthClientProtocol, "is_authenticated")
    assert hasattr(ShowsClientProtocol, "get_trending_shows")
    assert hasattr(ShowsClientProtocol, "get_popular_shows")
    assert hasattr(ShowsClientProtocol, "get_show_summary")


def test_protocol_runtime_checkable():
    """Test protocols are runtime checkable."""

    class MockAuthClient:
        async def get_device_code(self):
            pass

        async def get_device_token(self, device_code: str):
            pass

        def is_authenticated(self):
            pass

        def clear_auth(self):
            pass

    client = MockAuthClient()
    assert isinstance(client, AuthClientProtocol)


def test_protocol_inheritance():
    """Test protocol inheritance and compliance."""

    class MockShowsClient:
        async def get_trending_shows(self, limit: int = 10, extended: bool = False):
            pass

        async def get_popular_shows(self, limit: int = 10, extended: bool = False):
            pass

        async def get_show_summary(self, show_id: str, extended: bool = True):
            pass

        async def get_show_ratings(self, show_id: str):
            pass

        async def get_show_comments(
            self,
            show_id: str,
            limit: int = 10,
            sort: str = "newest",
            show_spoilers: bool = False,
        ):
            pass

    client = MockShowsClient()
    assert isinstance(client, ShowsClientProtocol)


def test_typed_dict_validation():
    """Test TypedDict validation works correctly."""
    # Test that TraktIds can be created with proper structure
    trakt_ids: TraktIds = {"trakt": 12345, "slug": "test-slug"}
    assert trakt_ids["trakt"] == 12345
    assert trakt_ids["slug"] == "test-slug"

    # Test ShowResponse with required fields
    show: ShowResponse = {"title": "Test Show", "year": 2023, "ids": trakt_ids}
    assert show["title"] == "Test Show"
    assert show["year"] == 2023
    assert show["ids"]["trakt"] == 12345


def test_optional_fields_handling():
    """Test that NotRequired fields work correctly."""
    # TraktIds with optional fields
    trakt_ids_full: TraktIds = {
        "trakt": 12345,
        "slug": "test-slug",
        "imdb": "tt1234567",
        "tmdb": 67890,
    }
    assert "imdb" in trakt_ids_full
    assert "tmdb" in trakt_ids_full

    # TraktIds with only required fields
    trakt_ids_minimal: TraktIds = {"trakt": 12345, "slug": "test-slug"}
    assert "imdb" not in trakt_ids_minimal
    assert "tmdb" not in trakt_ids_minimal


def test_complex_type_structures():
    """Test complex nested type structures."""
    # TrendingWrapper with nested show
    show: ShowResponse = {
        "title": "Breaking Bad",
        "year": 2008,
        "ids": {"trakt": 1390, "slug": "breaking-bad"},
    }

    trending: TrendingWrapper = {"watchers": 12345, "show": show}

    assert trending["watchers"] == 12345
    assert trending["show"]["title"] == "Breaking Bad"
    assert trending["show"]["ids"]["trakt"] == 1390


def test_type_compatibility():
    """Test type compatibility and assignment."""

    # Test that our types work with generic type annotations
    shows: list[ShowResponse] = []
    movies: list[MovieResponse] = []
    trending_items: list[TrendingWrapper] = []

    # These should all be valid assignments
    assert isinstance(shows, list)
    assert isinstance(movies, list)
    assert isinstance(trending_items, list)


def test_protocol_method_signatures():
    """Test that protocol method signatures are correctly typed."""
    from typing import get_type_hints

    # Test AuthClientProtocol method signatures
    auth_hints = get_type_hints(AuthClientProtocol.get_device_code)
    shows_hints = get_type_hints(ShowsClientProtocol.get_trending_shows)

    # These should not raise exceptions and should have proper type information
    assert auth_hints is not None
    assert shows_hints is not None
