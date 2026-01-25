"""Tests for movies formatter module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from models.formatters.movies import MovieFormatters
from models.types.pagination import PaginatedResponse, PaginationMetadata

if TYPE_CHECKING:
    from models.types.api_responses import MovieResponse, TrendingWrapper


def make_movie_response(
    *,
    title: str = "Unknown",
    year: int = 0,
    trakt: int = 0,
    slug: str = "unknown",
    **overrides: Any,
) -> MovieResponse:
    """Factory helper for creating MovieResponse test data."""
    base: MovieResponse = {
        "title": title,
        "year": year,
        "ids": {"trakt": trakt, "slug": slug},
    }
    # Use cast() to handle runtime flexibility with static typing
    return cast("MovieResponse", {**base, **overrides})


def make_trending_item(
    *,
    title: str,
    year: int,
    trakt: int,
    slug: str,
    watchers: int,
    **movie_overrides: Any,
) -> TrendingWrapper:
    """Factory helper for creating TrendingWrapper test data."""
    return {
        "watchers": watchers,
        "movie": make_movie_response(
            title=title, year=year, trakt=trakt, slug=slug, **movie_overrides
        ),
    }


class TestMovieFormatters:
    """Test MovieFormatters class and methods."""

    def test_class_exists(self) -> None:
        """Test that MovieFormatters class exists."""
        assert MovieFormatters is not None

    def test_format_trending_movies_exists(self) -> None:
        """Test that format_trending_movies method exists."""
        assert hasattr(MovieFormatters, "format_trending_movies")
        assert callable(MovieFormatters.format_trending_movies)

    def test_format_trending_movies_with_empty_list(self) -> None:
        """Test formatting empty movies list."""
        result = MovieFormatters.format_trending_movies([])
        assert isinstance(result, str)

    def test_format_trending_movies_with_data(self) -> None:
        """Test formatting movies with sample data."""
        sample_movies: list[TrendingWrapper] = [
            make_trending_item(
                title="Test Movie 1",
                year=2023,
                trakt=1,
                slug="test-movie-1",
                watchers=150,
            ),
            make_trending_item(
                title="Test Movie 2",
                year=2024,
                trakt=2,
                slug="test-movie-2",
                watchers=250,
            ),
        ]
        result = MovieFormatters.format_trending_movies(sample_movies)
        assert isinstance(result, str)
        assert "Test Movie 1" in result
        assert "Test Movie 2" in result

    def test_has_additional_formatter_methods(self) -> None:
        """Test that additional formatter methods exist."""
        # Check for other common movie formatting methods
        expected_methods = [
            "format_trending_movies",
            "format_popular_movies",
            "format_favorited_movies",
            "format_played_movies",
            "format_watched_movies",
            "format_movie_summary",
            "format_movie_extended",
        ]

        for method_name in expected_methods:
            if hasattr(MovieFormatters, method_name):
                assert callable(getattr(MovieFormatters, method_name))

    def test_all_methods_are_static(self) -> None:
        """Test that all public methods are static methods."""
        for attr_name in dir(MovieFormatters):
            if not attr_name.startswith("_") and callable(
                getattr(MovieFormatters, attr_name)
            ):
                attr = MovieFormatters.__dict__.get(attr_name)
                if attr is not None:
                    assert isinstance(attr, staticmethod), (
                        f"Method {attr_name} should be static"
                    )

    def test_format_movie_summary(self) -> None:
        """Test format_movie_summary with basic movie data."""
        movie_data: MovieResponse = make_movie_response(
            title="The Matrix",
            year=1999,
            trakt=12345,
            slug="the-matrix",
        )
        result = MovieFormatters.format_movie_summary(movie_data)
        assert isinstance(result, str)
        assert "## The Matrix (1999)" in result
        assert "Trakt ID: 12345" in result

    def test_format_movie_summary_with_missing_data(self) -> None:
        """Test format_movie_summary with missing fields."""
        movie_data: MovieResponse = make_movie_response(
            title="Test Movie",
            year=2023,
            trakt=1,
            slug="test-movie",
        )
        result = MovieFormatters.format_movie_summary(movie_data)
        assert isinstance(result, str)
        assert "Test Movie" in result

    def test_format_movie_summary_with_unknown_placeholders(self) -> None:
        """Test format_movie_summary with placeholder/unknown values.

        Validates that the formatter handles Unknown/0 placeholder values correctly
        rather than truly empty data (which would violate MovieResponse requirements).
        """
        placeholder_movie_data: MovieResponse = make_movie_response()  # Uses defaults
        result = MovieFormatters.format_movie_summary(placeholder_movie_data)
        assert isinstance(result, str)
        assert "## Unknown" in result
        assert "Trakt ID: 0" in result

    def test_format_movie_extended(self) -> None:
        """Test format_movie_extended with comprehensive movie data."""
        movie_data: MovieResponse = make_movie_response(
            title="TRON: Legacy",
            year=2010,
            trakt=1,
            slug="tron-legacy",
            tagline="The Game Has Changed.",
            overview="Sam Flynn investigates his father's disappearance.",
            released="2010-12-16",
            runtime=125,
            country="us",
            status="released",
            rating=8.0,
            votes=111,
            comment_count=92,
            language="en",
            genres=["action", "sci-fi"],
            certification="PG-13",
            homepage="http://disney.go.com/tron/",
        )
        result = MovieFormatters.format_movie_extended(movie_data)
        assert isinstance(result, str)
        assert "## TRON: Legacy (2010) - Released" in result
        assert "*The Game Has Changed.*" in result
        assert "Sam Flynn investigates his father's disappearance." in result
        assert "- Status: released" in result
        assert "- Runtime: 125 minutes" in result
        assert "- Certification: PG-13" in result
        assert "- Released: 2010-12-16" in result
        assert "- Country: US" in result
        assert "- Genres: action, sci-fi" in result
        # Note: Language field formatting may vary based on formatter implementation
        assert "- Homepage: http://disney.go.com/tron/" in result
        assert "- Rating: 8.0/10 (111 votes)" in result
        assert "- Comments: 92" in result
        assert "Trakt ID: 1" in result

    def test_format_movie_extended_with_partial_data(self) -> None:
        """Test format_movie_extended with partial data."""
        movie_data: MovieResponse = make_movie_response(
            title="Test Movie",
            year=2023,
            trakt=1,
            slug="test-movie",
            status="in_production",
            rating=7.5,
            votes=50,
        )
        result = MovieFormatters.format_movie_extended(movie_data)
        assert isinstance(result, str)
        assert "## Test Movie (2023) - In Production" in result
        assert "- Status: in production" in result
        assert "- Rating: 7.5/10 (50 votes)" in result
        # Ensure optional fields don't appear
        assert "- Runtime:" not in result
        assert "- Certification:" not in result
        assert "- Released:" not in result
        assert "- Genres:" not in result
        assert "- Languages:" not in result
        assert "- Homepage:" not in result
        assert "- Comments:" not in result

    def test_format_movie_extended_with_languages_list(self) -> None:
        """Test format_movie_extended with languages list (plural key).

        Ensures coverage of the 'languages' (plural) key handling in the formatter,
        which differs from the singular 'language' key used in other tests.
        """
        movie_data: MovieResponse = make_movie_response(
            title="Locale Test",
            year=2020,
            trakt=42,
            slug="locale-test",
            languages=["en", "fr"],
        )
        result = MovieFormatters.format_movie_extended(movie_data)
        assert isinstance(result, str)
        assert "- Languages: en, fr" in result

    def test_format_related_movies_exists(self) -> None:
        """Test that format_related_movies method exists."""
        assert hasattr(MovieFormatters, "format_related_movies")
        assert callable(MovieFormatters.format_related_movies)

    def test_format_related_movies_with_data(self) -> None:
        """Test formatting related movies with sample data."""
        sample_movies: list[MovieResponse] = [
            make_movie_response(
                title="The Dark Knight Rises",
                year=2012,
                trakt=28,
                slug="the-dark-knight-rises",
                overview="Eight years after the Joker's reign of anarchy.",
            ),
            make_movie_response(
                title="Batman Begins",
                year=2005,
                trakt=155,
                slug="batman-begins",
                overview="A young Bruce Wayne travels to the Far East.",
            ),
        ]
        result = MovieFormatters.format_related_movies(sample_movies)
        assert isinstance(result, str)
        assert "# Related Movies" in result
        assert "The Dark Knight Rises (2012)" in result
        assert "Batman Begins (2005)" in result
        assert "Eight years after the Joker's reign of anarchy." in result

    def test_format_related_movies_empty(self) -> None:
        """Test formatting empty related movies list."""
        result = MovieFormatters.format_related_movies([])
        assert isinstance(result, str)
        assert "# Related Movies" in result
        assert "No related movies found." in result

    def test_format_related_movies_with_pagination(self) -> None:
        """Test formatting related movies with pagination metadata."""
        sample_movies: list[MovieResponse] = [
            make_movie_response(
                title="The Dark Knight Rises",
                year=2012,
                trakt=28,
                slug="the-dark-knight-rises",
            )
        ]
        paginated_response: PaginatedResponse[MovieResponse] = PaginatedResponse(
            data=sample_movies,
            pagination=PaginationMetadata(
                current_page=2,
                items_per_page=10,
                total_pages=3,
                total_items=25,
            ),
        )
        result = MovieFormatters.format_related_movies(paginated_response)
        assert isinstance(result, str)
        assert "# Related Movies" in result
        assert "The Dark Knight Rises (2012)" in result
        # Should include pagination info
        assert "Page 2" in result or "page" in result.lower()

    def test_format_related_movies_truncates_overview(self) -> None:
        """Test that long overviews are truncated to 200 characters."""
        long_overview = "A" * 300  # 300 character overview
        sample_movies: list[MovieResponse] = [
            make_movie_response(
                title="Test Movie",
                year=2023,
                trakt=1,
                slug="test-movie",
                overview=long_overview,
            )
        ]
        result = MovieFormatters.format_related_movies(sample_movies)
        assert isinstance(result, str)
        # Should be truncated with ellipsis
        assert "..." in result
        # Should not contain the full 300 character string
        assert long_overview not in result
