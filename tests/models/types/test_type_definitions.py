"""Tests for TypedDict type definitions."""

from typing import get_type_hints

from models.types import (
    CommentResponse,
    MovieResponse,
    SearchResult,
    ShowResponse,
    TraktIdsDict,
    TraktRating,
    TrendingWrapper,
)


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


def test_trakt_rating_structure():
    """Test TraktRating has required fields."""
    hints = get_type_hints(TraktRating)
    assert "rating" in hints
    assert "votes" in hints
    assert "distribution" in hints
    assert hints["rating"] is float
    assert hints["votes"] is int


def test_typed_dict_validation():
    """Test TypedDict validation works correctly."""
    trakt_ids: TraktIdsDict = {"trakt": 12345, "slug": "test-slug"}
    assert trakt_ids["trakt"] == 12345
    assert trakt_ids["slug"] == "test-slug"

    show: ShowResponse = {"title": "Test Show", "year": 2023, "ids": trakt_ids}
    assert show["title"] == "Test Show"
    assert show["year"] == 2023
    assert show["ids"]["trakt"] == 12345


def test_optional_fields_handling():
    """Test that NotRequired fields work correctly."""
    trakt_ids_full: TraktIdsDict = {
        "trakt": 12345,
        "slug": "test-slug",
        "imdb": "tt1234567",
        "tmdb": 67890,
    }
    assert "imdb" in trakt_ids_full
    assert "tmdb" in trakt_ids_full

    trakt_ids_minimal: TraktIdsDict = {"trakt": 12345, "slug": "test-slug"}
    assert "imdb" not in trakt_ids_minimal
    assert "tmdb" not in trakt_ids_minimal


def test_complex_type_structures():
    """Test complex nested type structures."""
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
    shows: list[ShowResponse] = []
    movies: list[MovieResponse] = []
    trending_items: list[TrendingWrapper] = []

    assert isinstance(shows, list)
    assert isinstance(movies, list)
    assert isinstance(trending_items, list)
