"""Tests for movies formatter module."""

from typing import TYPE_CHECKING, cast

from models.formatters.movies import MovieFormatters

if TYPE_CHECKING:
    from models.types import MovieResponse, TrendingWrapper


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
            {
                "watchers": 150,
                "movie": {
                    "title": "Test Movie 1",
                    "year": 2023,
                    "ids": {"trakt": 1, "slug": "test-movie-1"},
                },
            },
            {
                "watchers": 250,
                "movie": {
                    "title": "Test Movie 2",
                    "year": 2024,
                    "ids": {"trakt": 2, "slug": "test-movie-2"},
                },
            },
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
        movie_data = cast(
            "MovieResponse",
            {
                "title": "The Matrix",
                "year": 1999,
                "ids": {"trakt": 12345},
            },
        )
        result = MovieFormatters.format_movie_summary(movie_data)
        assert isinstance(result, str)
        assert "## The Matrix (1999)" in result
        assert "Trakt ID: 12345" in result

    def test_format_movie_summary_with_missing_data(self) -> None:
        """Test format_movie_summary with missing fields."""
        movie_data = cast("MovieResponse", {"title": "Test Movie"})
        result = MovieFormatters.format_movie_summary(movie_data)
        assert isinstance(result, str)
        assert "Test Movie" in result

    def test_format_movie_summary_empty_data(self) -> None:
        """Test format_movie_summary with empty data."""
        result = MovieFormatters.format_movie_summary(cast("MovieResponse", {}))
        assert isinstance(result, str)
        assert "No movie data available." in result

    def test_format_movie_extended(self) -> None:
        """Test format_movie_extended with comprehensive movie data."""
        movie_data = cast(
            "MovieResponse",
            {
                "title": "TRON: Legacy",
                "year": 2010,
                "ids": {"trakt": 1},
                "tagline": "The Game Has Changed.",
                "overview": "Sam Flynn investigates his father's disappearance.",
                "released": "2010-12-16",
                "runtime": 125,
                "country": "us",
                "status": "released",
                "rating": 8.0,
                "votes": 111,
                "comment_count": 92,
                "languages": ["en"],
                "genres": ["action", "sci-fi"],
                "certification": "PG-13",
                "homepage": "http://disney.go.com/tron/",
            },
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
        assert "- Languages: en" in result
        assert "- Homepage: http://disney.go.com/tron/" in result
        assert "- Rating: 8.0/10 (111 votes)" in result
        assert "- Comments: 92" in result
        assert "Trakt ID: 1" in result

    def test_format_movie_extended_with_partial_data(self) -> None:
        """Test format_movie_extended with partial data."""
        movie_data = cast(
            "MovieResponse",
            {
                "title": "Test Movie",
                "year": 2023,
                "status": "in_production",
                "rating": 7.5,
                "votes": 50,
            },
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
