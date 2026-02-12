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

    def test_format_device_auth_instructions_exists(self) -> None:
        """Test that format_device_auth_instructions method exists."""
        assert hasattr(AuthFormatters, "format_device_auth_instructions")
        assert callable(AuthFormatters.format_device_auth_instructions)

    def test_format_device_auth_instructions_includes_direct_link(self) -> None:
        """Test that instructions include direct link with code."""
        result = AuthFormatters.format_device_auth_instructions(
            user_code="ABC123",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
        )
        assert isinstance(result, str)
        # Should include direct link format: verification_url/user_code
        assert "https://trakt.tv/activate/ABC123" in result
        # Should also include fallback with manual code entry
        assert "ABC123" in result
        assert "https://trakt.tv/activate" in result

    def test_format_device_auth_instructions_includes_expiration(self) -> None:
        """Test that instructions include expiration time in minutes."""
        result = AuthFormatters.format_device_auth_instructions(
            user_code="XYZ789",
            verification_url="https://trakt.tv/activate",
            expires_in=600,  # 10 minutes
        )
        assert "10 minutes" in result

    def test_format_device_auth_instructions_is_static(self) -> None:
        """Test that format_device_auth_instructions is a static method."""
        assert isinstance(
            AuthFormatters.__dict__["format_device_auth_instructions"], staticmethod
        )
