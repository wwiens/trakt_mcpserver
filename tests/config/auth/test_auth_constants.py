"""Tests for auth constants module."""

from config.auth.constants import (
    AUTH_EXPIRATION,
    AUTH_POLL_INTERVAL,
    AUTH_VERIFICATION_URL,
)


class TestAuthConstants:
    """Test authentication-related constants."""

    def test_auth_poll_interval_value(self) -> None:
        """Test AUTH_POLL_INTERVAL has correct value and type."""
        assert AUTH_POLL_INTERVAL == 5
        assert isinstance(AUTH_POLL_INTERVAL, int)

    def test_auth_expiration_value(self) -> None:
        """Test AUTH_EXPIRATION has correct value and type."""
        assert AUTH_EXPIRATION == 600
        assert isinstance(AUTH_EXPIRATION, int)
        # Verify it's 10 minutes in seconds
        assert AUTH_EXPIRATION == 10 * 60

    def test_auth_verification_url_value(self) -> None:
        """Test AUTH_VERIFICATION_URL has correct value and type."""
        assert AUTH_VERIFICATION_URL == "https://trakt.tv/activate"
        assert isinstance(AUTH_VERIFICATION_URL, str)
        # Verify it's a valid URL format
        assert AUTH_VERIFICATION_URL.startswith("https://")
        assert "trakt.tv" in AUTH_VERIFICATION_URL

    def test_auth_poll_interval_is_reasonable(self) -> None:
        """Test AUTH_POLL_INTERVAL is within reasonable bounds."""
        # Should be positive
        assert AUTH_POLL_INTERVAL > 0
        # Should not be too frequent (< 1 second) or too slow (> 30 seconds)
        assert 1 <= AUTH_POLL_INTERVAL <= 30

    def test_auth_expiration_is_reasonable(self) -> None:
        """Test AUTH_EXPIRATION is within reasonable bounds."""
        # Should be positive
        assert AUTH_EXPIRATION > 0
        # Should be at least 5 minutes and at most 30 minutes
        assert 300 <= AUTH_EXPIRATION <= 1800

    def test_auth_timing_relationship(self) -> None:
        """Test that AUTH_EXPIRATION is much larger than AUTH_POLL_INTERVAL."""
        # Expiration should be at least 10 times the poll interval
        assert AUTH_EXPIRATION >= AUTH_POLL_INTERVAL * 10
        # This ensures reasonable number of polling attempts
        max_polls = AUTH_EXPIRATION // AUTH_POLL_INTERVAL
        assert max_polls >= 10  # At least 10 polling attempts possible

    def test_constants_are_immutable_types(self) -> None:
        """Test that all auth constants use immutable types."""
        constants = [
            AUTH_POLL_INTERVAL,
            AUTH_EXPIRATION,
            AUTH_VERIFICATION_URL,
        ]

        for constant in constants:
            # Should be one of the basic immutable types
            assert isinstance(constant, int | str | float | bool | tuple)
