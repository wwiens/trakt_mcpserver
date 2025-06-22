"""Tests for auth formatter module."""

from models.formatters.auth import AuthFormatters


class TestAuthFormatters:
    """Test AuthFormatters class and methods."""

    def test_class_exists(self) -> None:
        """Test that AuthFormatters class exists."""
        assert AuthFormatters is not None

    def test_format_auth_status_exists(self) -> None:
        """Test that format_auth_status method exists."""
        assert hasattr(AuthFormatters, "format_auth_status")
        assert callable(AuthFormatters.format_auth_status)

    def test_format_auth_status_authenticated(self) -> None:
        """Test formatting authenticated status."""
        result = AuthFormatters.format_auth_status(True, 1234567890)
        assert isinstance(result, str)
        assert "authenticated" in result.lower()
        assert "1234567890" in result

    def test_format_auth_status_not_authenticated(self) -> None:
        """Test formatting non-authenticated status."""
        result = AuthFormatters.format_auth_status(False)
        assert isinstance(result, str)
        assert (
            "not authenticated" in result.lower() or "unauthenticated" in result.lower()
        )

    def test_format_auth_status_with_none_expires(self) -> None:
        """Test formatting authenticated status with None expiration."""
        result = AuthFormatters.format_auth_status(True, None)
        assert isinstance(result, str)
        assert "authenticated" in result.lower()

    def test_all_methods_are_static(self) -> None:
        """Test that all methods are static methods."""
        # Check that format_auth_status is a static method
        assert isinstance(AuthFormatters.__dict__["format_auth_status"], staticmethod)
