"""Tests for pagination models."""

from typing import Any

import pytest

from models.types.pagination import (
    PaginatedResponse,
    PaginationMetadata,
    PaginationParams,
)


class TestPaginationParams:
    """Test cases for PaginationParams model."""

    def test_default_values(self) -> None:
        """Test default parameter values."""
        params = PaginationParams()
        assert params.page == 1
        assert params.limit == 10  # DEFAULT_LIMIT from config

    def test_custom_values(self) -> None:
        """Test custom parameter values."""
        params = PaginationParams(page=3, limit=25)
        assert params.page == 3
        assert params.limit == 25

    def test_validation_positive_integers(self) -> None:
        """Test validation requires positive integers."""
        with pytest.raises(ValueError):
            PaginationParams(page=0)

        with pytest.raises(ValueError):
            PaginationParams(page=-1)

        with pytest.raises(ValueError):
            PaginationParams(limit=0)

        with pytest.raises(ValueError):
            PaginationParams(limit=-5)


class TestPaginationMetadata:
    """Test cases for PaginationMetadata model."""

    def test_basic_creation(self) -> None:
        """Test basic metadata creation."""
        metadata = PaginationMetadata(
            current_page=2, items_per_page=10, total_pages=5, total_items=50
        )
        assert metadata.current_page == 2
        assert metadata.items_per_page == 10
        assert metadata.total_pages == 5
        assert metadata.total_items == 50

    def test_first_page_properties(self) -> None:
        """Test properties when on first page."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=3, total_items=25
        )

        # First page boundary conditions
        assert not metadata.has_previous_page
        assert metadata.has_next_page
        assert metadata.previous_page is None
        assert metadata.next_page == 2

    def test_last_page_properties(self) -> None:
        """Test properties when on last page."""
        metadata = PaginationMetadata(
            current_page=3, items_per_page=10, total_pages=3, total_items=25
        )

        # Last page boundary conditions
        assert metadata.has_previous_page
        assert not metadata.has_next_page
        assert metadata.previous_page == 2
        assert metadata.next_page is None

    def test_middle_page_properties(self) -> None:
        """Test properties when on middle page."""
        metadata = PaginationMetadata(
            current_page=2, items_per_page=10, total_pages=4, total_items=35
        )

        # Middle page conditions
        assert metadata.has_previous_page
        assert metadata.has_next_page
        assert metadata.previous_page == 1
        assert metadata.next_page == 3

    def test_single_page_properties(self) -> None:
        """Test properties when there's only one page."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=5
        )

        # Single page boundary conditions
        assert not metadata.has_previous_page
        assert not metadata.has_next_page
        assert metadata.previous_page is None
        assert metadata.next_page is None

    def test_zero_total_items(self) -> None:
        """Test handling of zero total items."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=0
        )
        assert metadata.total_items == 0
        assert not metadata.has_next_page
        assert not metadata.has_previous_page


class TestPaginatedResponse:
    """Test cases for PaginatedResponse model."""

    def test_basic_paginated_response(self) -> None:
        """Test basic paginated response creation."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=2, total_pages=3, total_items=5
        )

        response = PaginatedResponse[str](data=["item1", "item2"], pagination=metadata)

        assert len(response.data) == 2
        assert response.data[0] == "item1"
        assert response.data[1] == "item2"
        assert not response.is_empty
        assert not response.is_single_page

    def test_empty_page_properties(self) -> None:
        """Test properties when current page is empty."""
        metadata = PaginationMetadata(
            current_page=3, items_per_page=10, total_pages=3, total_items=25
        )

        response = PaginatedResponse[str](data=[], pagination=metadata)

        assert response.is_empty
        assert not response.is_single_page

    def test_single_page_properties(self) -> None:
        """Test properties for single page responses."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=3
        )

        response = PaginatedResponse[str](
            data=["item1", "item2", "item3"], pagination=metadata
        )

        assert not response.is_empty
        assert response.is_single_page

    def test_page_info_summary_single_page(self) -> None:
        """Test page_info_summary for single page."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=5
        )

        response = PaginatedResponse[str](
            data=["a", "b", "c", "d", "e"], pagination=metadata
        )

        summary = response.page_info_summary()
        assert summary == "5 total items"

    def test_page_info_summary_multi_page_with_data(self) -> None:
        """Test page_info_summary for multi-page with data."""
        metadata = PaginationMetadata(
            current_page=2, items_per_page=3, total_pages=4, total_items=10
        )

        response = PaginatedResponse[str](
            data=["item4", "item5", "item6"], pagination=metadata
        )

        summary = response.page_info_summary()
        assert summary == "Page 2 of 4 (items 4-6 of 10)"

    def test_page_info_summary_empty_page(self) -> None:
        """Test page_info_summary for empty page in multi-page response."""
        metadata = PaginationMetadata(
            current_page=3, items_per_page=10, total_pages=3, total_items=25
        )

        # This could happen if items were deleted between requests
        response = PaginatedResponse[str](data=[], pagination=metadata)

        summary = response.page_info_summary()
        expected = "Page 3 of 3 (no items on this page; 25 total)"
        assert summary == expected

    def test_page_info_summary_first_page_full(self) -> None:
        """Test page_info_summary for first page with full data."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=5, total_pages=3, total_items=12
        )

        response = PaginatedResponse[str](
            data=["1", "2", "3", "4", "5"], pagination=metadata
        )

        summary = response.page_info_summary()
        assert summary == "Page 1 of 3 (items 1-5 of 12)"

    def test_page_info_summary_last_page_partial(self) -> None:
        """Test page_info_summary for last page with partial data."""
        metadata = PaginationMetadata(
            current_page=3, items_per_page=5, total_pages=3, total_items=12
        )

        response = PaginatedResponse[str](
            data=["11", "12"],  # Only 2 items on last page
            pagination=metadata,
        )

        summary = response.page_info_summary()
        assert summary == "Page 3 of 3 (items 11-12 of 12)"

    def test_page_info_summary_edge_case_single_item(self) -> None:
        """Test page_info_summary with single item on page."""
        metadata = PaginationMetadata(
            current_page=2, items_per_page=5, total_pages=3, total_items=11
        )

        response = PaginatedResponse[str](
            data=["item6"],  # Single item on this page
            pagination=metadata,
        )

        summary = response.page_info_summary()
        assert summary == "Page 2 of 3 (items 6-6 of 11)"

    @pytest.mark.parametrize(
        "page,total_pages,expected_has_next,expected_has_prev",
        [
            (1, 1, False, False),  # Single page
            (1, 3, True, False),  # First of multiple pages
            (2, 3, True, True),  # Middle page
            (3, 3, False, True),  # Last page
            (1, 10, True, False),  # First page of many
            (10, 10, False, True),  # Last page of many
        ],
    )
    def test_navigation_properties_parametrized(
        self,
        page: int,
        total_pages: int,
        expected_has_next: bool,
        expected_has_prev: bool,
    ) -> None:
        """Test navigation properties across various page scenarios."""
        metadata = PaginationMetadata(
            current_page=page,
            items_per_page=10,
            total_pages=total_pages,
            total_items=total_pages * 10,  # Full pages for simplicity
        )

        _response = PaginatedResponse[str](
            data=["item"] * 10,  # Mock full page
            pagination=metadata,
        )

        assert metadata.has_next_page == expected_has_next
        assert metadata.has_previous_page == expected_has_prev

        if expected_has_next:
            assert metadata.next_page == page + 1
        else:
            assert metadata.next_page is None

        if expected_has_prev:
            assert metadata.previous_page == page - 1
        else:
            assert metadata.previous_page is None

    def test_page_info_calculation_edge_cases(self) -> None:
        """Test edge cases in page info calculations."""
        # Test case where data length is less than items_per_page due to filtering/deletion
        metadata = PaginationMetadata(
            current_page=2, items_per_page=10, total_pages=2, total_items=15
        )

        # Simulate case where some items were filtered out or deleted
        response = PaginatedResponse[str](
            data=["item11", "item12"],  # Only 2 items instead of expected 5
            pagination=metadata,
        )

        summary = response.page_info_summary()
        # Should still calculate correctly based on actual data length
        assert summary == "Page 2 of 2 (items 11-12 of 15)"

    def test_zero_items_edge_case(self) -> None:
        """Test handling when total_items is 0."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=0
        )

        response = PaginatedResponse[str](data=[], pagination=metadata)

        assert response.is_empty
        assert response.is_single_page
        summary = response.page_info_summary()
        assert summary == "0 total items"

    def test_generic_type_support(self) -> None:
        """Test that PaginatedResponse works with different types."""
        metadata = PaginationMetadata(
            current_page=1, items_per_page=3, total_pages=1, total_items=3
        )

        # Test with integers
        int_response = PaginatedResponse[int](data=[1, 2, 3], pagination=metadata)
        assert isinstance(int_response.data[0], int)

        # Test with dictionaries
        dict_response = PaginatedResponse[dict[str, Any]](
            data=[{"id": 1}, {"id": 2}], pagination=metadata
        )
        assert isinstance(dict_response.data[0], dict)
        assert dict_response.data[0]["id"] == 1

    def test_field_validation_constraints(self) -> None:
        """Test that field validation works correctly."""
        # Valid metadata should work
        metadata = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=5
        )
        assert metadata.total_items == 5

        # total_items with 0 should be allowed
        metadata_zero = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=0
        )
        assert metadata_zero.total_items == 0

        # Negative total_items should fail
        with pytest.raises(ValueError):
            PaginationMetadata(
                current_page=1, items_per_page=10, total_pages=1, total_items=-1
            )
