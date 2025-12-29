"""Tests for API constants module."""

import pytest

from config.api.constants import (
    DEFAULT_FETCH_ALL_LIMIT,
    DEFAULT_LIMIT,
    MAX_API_PAGE_SIZE,
    EffectiveLimit,
    effective_limit,
)


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


class TestEffectiveLimit:
    """Test effective_limit function."""

    def test_positive_limit_returns_same_values(self) -> None:
        """Test that positive limit returns the same value for both api_limit and max_items."""
        result = effective_limit(10)
        assert isinstance(result, EffectiveLimit)
        assert result.api_limit == 10
        assert result.max_items == 10

    def test_zero_limit_returns_fetch_all_values(self) -> None:
        """Test that limit=0 returns max page size and fetch all limit."""
        result = effective_limit(0)
        assert result.api_limit == MAX_API_PAGE_SIZE
        assert result.max_items == DEFAULT_FETCH_ALL_LIMIT

    def test_negative_limit_raises_value_error(self) -> None:
        """Test that negative limit raises ValueError."""
        with pytest.raises(ValueError, match="limit must be >= 0, got -1"):
            effective_limit(-1)

    def test_negative_large_limit_raises_value_error(self) -> None:
        """Test that large negative limit raises ValueError."""
        with pytest.raises(ValueError, match="limit must be >= 0, got -100"):
            effective_limit(-100)

    def test_various_positive_limits(self) -> None:
        """Test various positive limit values."""
        for limit in [1, 5, 50, 100]:
            result = effective_limit(limit)
            assert result.api_limit == limit
            assert result.max_items == limit

    def test_effective_limit_named_tuple_fields(self) -> None:
        """Test that EffectiveLimit has correct named tuple fields."""
        result = effective_limit(25)
        # Test field access by name
        assert result.api_limit == 25
        assert result.max_items == 25
        # Test tuple unpacking still works
        api_limit, max_items = result
        assert api_limit == 25
        assert max_items == 25
