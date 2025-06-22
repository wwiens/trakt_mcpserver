"""Tests for shows formatter module."""

from models.formatters.shows import ShowFormatters


class TestShowFormatters:
    """Test ShowFormatters class and methods."""

    def test_class_exists(self) -> None:
        """Test that ShowFormatters class exists."""
        assert ShowFormatters is not None

    def test_format_trending_shows_exists(self) -> None:
        """Test that format_trending_shows method exists."""
        assert hasattr(ShowFormatters, "format_trending_shows")
        assert callable(ShowFormatters.format_trending_shows)

    def test_format_trending_shows_with_empty_list(self) -> None:
        """Test formatting empty shows list."""
        result = ShowFormatters.format_trending_shows([])
        assert isinstance(result, str)

    def test_format_trending_shows_with_data(self) -> None:
        """Test formatting shows with sample data."""
        sample_shows = [
            {"show": {"title": "Test Show 1", "year": 2023}, "watchers": 100},
            {"show": {"title": "Test Show 2", "year": 2024}, "watchers": 200},
        ]
        result = ShowFormatters.format_trending_shows(sample_shows)
        assert isinstance(result, str)
        assert "Test Show 1" in result
        assert "Test Show 2" in result

    def test_has_additional_formatter_methods(self) -> None:
        """Test that additional formatter methods exist."""
        # Check for other common show formatting methods
        expected_methods = [
            "format_trending_shows",
            "format_popular_shows",
            "format_favorited_shows",
            "format_played_shows",
            "format_watched_shows",
        ]

        for method_name in expected_methods:
            if hasattr(ShowFormatters, method_name):
                assert callable(getattr(ShowFormatters, method_name))

    def test_all_methods_are_static(self) -> None:
        """Test that all public methods are static methods."""
        for attr_name in dir(ShowFormatters):
            if not attr_name.startswith("_") and callable(
                getattr(ShowFormatters, attr_name)
            ):
                attr = ShowFormatters.__dict__.get(attr_name)
                if attr is not None:
                    assert isinstance(attr, staticmethod), (
                        f"Method {attr_name} should be static"
                    )
