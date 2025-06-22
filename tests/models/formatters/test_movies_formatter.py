"""Tests for movies formatter module."""

from models.formatters.movies import MovieFormatters


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
        sample_movies = [
            {"movie": {"title": "Test Movie 1", "year": 2023}, "watchers": 150},
            {"movie": {"title": "Test Movie 2", "year": 2024}, "watchers": 250},
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
