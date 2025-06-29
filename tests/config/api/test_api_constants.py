"""Tests for API constants module."""

from config.api.constants import DEFAULT_LIMIT


class TestApiConstants:
    """Test API-related constants."""

    def test_default_limit_value(self) -> None:
        """Test DEFAULT_LIMIT has correct value and type."""
        assert DEFAULT_LIMIT == 10
        assert isinstance(DEFAULT_LIMIT, int)

    def test_default_limit_is_reasonable(self) -> None:
        """Test DEFAULT_LIMIT is within reasonable bounds."""
        # Should be positive
        assert DEFAULT_LIMIT > 0
        # Should not be too small (< 1) or too large (> 100)
        assert 1 <= DEFAULT_LIMIT <= 100

    def test_constant_is_immutable_type(self) -> None:
        """Test that DEFAULT_LIMIT uses immutable type."""
        assert isinstance(DEFAULT_LIMIT, int | str | float | bool | tuple)
