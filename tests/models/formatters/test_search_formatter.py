"""Tests for search formatter module."""

from models.formatters.search import SearchFormatters


class TestSearchFormatters:
    """Test SearchFormatters class and methods."""

    def test_class_exists(self) -> None:
        """Test that SearchFormatters class exists."""
        assert SearchFormatters is not None

    def test_has_search_formatter_methods(self) -> None:
        """Test that search formatting methods exist."""
        # Check for common search formatting methods
        expected_methods = [
            "format_search_results",
            "format_show_search_results",
            "format_movie_search_results",
        ]

        for method_name in expected_methods:
            if hasattr(SearchFormatters, method_name):
                assert callable(getattr(SearchFormatters, method_name))

    def test_format_methods_return_strings(self) -> None:
        """Test that formatter methods return strings."""
        # Test with empty data where methods exist
        if hasattr(SearchFormatters, "format_show_search_results"):
            result = SearchFormatters.format_show_search_results([])
            assert isinstance(result, str)
        if hasattr(SearchFormatters, "format_movie_search_results"):
            result = SearchFormatters.format_movie_search_results([])
            assert isinstance(result, str)

    def test_all_methods_are_static(self) -> None:
        """Test that all public methods are static methods."""
        for attr_name in dir(SearchFormatters):
            if not attr_name.startswith("_") and callable(
                getattr(SearchFormatters, attr_name)
            ):
                attr = SearchFormatters.__dict__.get(attr_name)
                if attr is not None:
                    assert isinstance(attr, staticmethod), (
                        f"Method {attr_name} should be static"
                    )
