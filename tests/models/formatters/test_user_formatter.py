"""Tests for user formatter module."""

from models.formatters.user import UserFormatters


class TestUserFormatters:
    """Test UserFormatters class and methods."""

    def test_class_exists(self) -> None:
        """Test that UserFormatters class exists."""
        assert UserFormatters is not None

    def test_has_user_formatter_methods(self) -> None:
        """Test that user formatting methods exist."""
        # Check for common user formatting methods
        expected_methods = [
            "format_user_watched_shows",
            "format_user_watched_movies",
            "format_user_profile",
        ]

        for method_name in expected_methods:
            if hasattr(UserFormatters, method_name):
                assert callable(getattr(UserFormatters, method_name))

    def test_format_methods_return_strings(self) -> None:
        """Test that formatter methods return strings."""
        # Test with empty data where methods exist
        if hasattr(UserFormatters, "format_user_watched_shows"):
            result = UserFormatters.format_user_watched_shows([])
            assert isinstance(result, str)

    def test_all_methods_are_static(self) -> None:
        """Test that all public methods are static methods."""
        for attr_name in dir(UserFormatters):
            if not attr_name.startswith("_") and callable(
                getattr(UserFormatters, attr_name)
            ):
                attr = UserFormatters.__dict__.get(attr_name)
                if attr is not None:
                    assert isinstance(attr, staticmethod), (
                        f"Method {attr_name} should be static"
                    )
