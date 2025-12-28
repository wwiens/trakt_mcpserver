"""Tests for pagination validation across server tools.

These tests verify that limit=0 is correctly rejected when page is specified,
since limit=0 means "fetch all" which requires auto-pagination (page=None).
"""

import pytest
from pydantic import ValidationError

from server.base import LimitOnly, PeriodParams
from server.search.tools import QueryParam


class TestLimitOnlyValidation:
    """Test LimitOnly model validation for limit=0 with page specified."""

    def test_limit_zero_page_none_allowed(self) -> None:
        """Test that limit=0 with page=None is allowed (auto-pagination mode)."""
        params = LimitOnly(limit=0, page=None)
        assert params.limit == 0
        assert params.page is None

    def test_limit_zero_page_specified_rejected(self) -> None:
        """Test that limit=0 with page specified is rejected."""
        with pytest.raises(
            ValidationError, match="limit must be > 0 when page is specified"
        ):
            LimitOnly(limit=0, page=1)

    def test_positive_limit_with_page_allowed(self) -> None:
        """Test that positive limit with page specified is allowed."""
        params = LimitOnly(limit=10, page=1)
        assert params.limit == 10
        assert params.page == 1

    def test_positive_limit_without_page_allowed(self) -> None:
        """Test that positive limit without page is allowed."""
        params = LimitOnly(limit=50)
        assert params.limit == 50
        assert params.page is None


class TestPeriodParamsValidation:
    """Test PeriodParams model validation for limit=0 with page specified."""

    def test_limit_zero_page_none_allowed(self) -> None:
        """Test that limit=0 with page=None is allowed (auto-pagination mode)."""
        params = PeriodParams(limit=0, period="weekly", page=None)
        assert params.limit == 0
        assert params.page is None

    def test_limit_zero_page_specified_rejected(self) -> None:
        """Test that limit=0 with page specified is rejected."""
        with pytest.raises(
            ValidationError, match="limit must be > 0 when page is specified"
        ):
            PeriodParams(limit=0, period="weekly", page=1)

    def test_positive_limit_with_page_allowed(self) -> None:
        """Test that positive limit with page specified is allowed."""
        params = PeriodParams(limit=25, period="weekly", page=3)
        assert params.limit == 25
        assert params.page == 3


class TestQueryParamValidation:
    """Test QueryParam model validation for limit=0 with page specified."""

    def test_limit_zero_page_none_allowed(self) -> None:
        """Test that limit=0 with page=None is allowed (auto-pagination mode)."""
        params = QueryParam(query="test", limit=0, page=None)
        assert params.limit == 0
        assert params.page is None

    def test_limit_zero_page_specified_rejected(self) -> None:
        """Test that limit=0 with page specified is rejected."""
        with pytest.raises(
            ValidationError, match="limit must be > 0 when page is specified"
        ):
            QueryParam(query="test", limit=0, page=1)

    def test_positive_limit_with_page_allowed(self) -> None:
        """Test that positive limit with page specified is allowed."""
        params = QueryParam(query="test", limit=10, page=1)
        assert params.limit == 10
        assert params.page == 1


class TestEdgeCases:
    """Test edge cases for pagination validation."""

    def test_limit_one_with_page_allowed(self) -> None:
        """Test that limit=1 (minimum valid) with page is allowed."""
        params = LimitOnly(limit=1, page=1)
        assert params.limit == 1
        assert params.page == 1

    def test_limit_max_with_page_allowed(self) -> None:
        """Test that limit=100 (maximum) with page is allowed."""
        params = LimitOnly(limit=100, page=1)
        assert params.limit == 100
        assert params.page == 1

    def test_limit_zero_various_pages_rejected(self) -> None:
        """Test that limit=0 with various page numbers is rejected."""
        for page in [1, 2, 5, 10, 100]:
            with pytest.raises(ValidationError):
                LimitOnly(limit=0, page=page)

    def test_negative_limit_rejected_by_field_constraint(self) -> None:
        """Test that negative limit is rejected by ge=0 field constraint."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            LimitOnly(limit=-1, page=None)

    def test_limit_exceeds_max_rejected(self) -> None:
        """Test that limit > 100 is rejected by le=100 field constraint."""
        with pytest.raises(ValidationError, match="less than or equal to 100"):
            LimitOnly(limit=101, page=None)

    def test_page_zero_rejected_by_field_constraint(self) -> None:
        """Test that page=0 is rejected by ge=1 field constraint."""
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            LimitOnly(limit=10, page=0)

    def test_page_zero_rejected_for_period_params(self) -> None:
        """Test that page=0 is rejected by ge=1 field constraint for PeriodParams."""
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            PeriodParams(limit=10, period="weekly", page=0)

    def test_page_zero_rejected_for_query_param(self) -> None:
        """Test that page=0 is rejected by ge=1 field constraint for QueryParam."""
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            QueryParam(query="test", limit=10, page=0)
