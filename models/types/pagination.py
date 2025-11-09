"""Pagination models for Trakt API responses."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, PositiveInt

from config.api import DEFAULT_LIMIT

# Generic type for pagination data
T = TypeVar("T")


class PaginationParams(BaseModel):
    """Request parameters for paginated API calls.

    Follows Trakt API pagination query parameters:
    - page: Page number to retrieve (1-based)
    - limit: Number of items per page
    """

    page: PositiveInt = Field(default=1, description="Page number (1-based)")
    limit: PositiveInt = Field(
        default=DEFAULT_LIMIT, description="Number of items per page"
    )


class PaginationMetadata(BaseModel):
    """Pagination metadata extracted from Trakt API response headers.

    Maps to X-Pagination-* headers:
    - X-Pagination-Page -> current_page
    - X-Pagination-Limit -> items_per_page
    - X-Pagination-Page-Count -> total_pages
    - X-Pagination-Item-Count -> total_items
    """

    current_page: int = Field(ge=1, description="Current page number")
    items_per_page: int = Field(ge=1, description="Items returned per page")
    total_pages: int = Field(ge=0, description="Total number of pages")
    total_items: int = Field(
        ge=0,
        description="Total number of items across all pages",
    )

    @property
    def has_next_page(self) -> bool:
        """Check if there are more pages available."""
        return self.current_page < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        """Check if there are previous pages available."""
        return self.current_page > 1

    def next_page(self) -> int | None:
        """Get the next page number, or None if on last page."""
        return self.current_page + 1 if self.has_next_page else None

    def previous_page(self) -> int | None:
        """Get the previous page number, or None if on first page."""
        return self.current_page - 1 if self.has_previous_page else None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated API responses.

    Combines the actual data with pagination metadata for easier
    navigation and display of paginated results.
    """

    data: list[T] = Field(description="List of items for current page")
    pagination: PaginationMetadata = Field(description="Pagination information")

    @property
    def is_empty(self) -> bool:
        """Check if the current page has no data."""
        return len(self.data) == 0

    @property
    def is_single_page(self) -> bool:
        """Check if all results fit in a single page."""
        return self.pagination.total_pages <= 1

    def page_info_summary(self) -> str:
        """Get a human-readable summary of pagination state."""
        if self.is_single_page:
            return f"{self.pagination.total_items} total items"

        if len(self.data) == 0:
            return (
                f"Page {self.pagination.current_page} of "
                f"{self.pagination.total_pages} "
                f"(no items on this page; "
                f"{self.pagination.total_items} total)"
            )

        start_item = (
            self.pagination.current_page - 1
        ) * self.pagination.items_per_page + 1
        end_item = min(start_item + len(self.data) - 1, self.pagination.total_items)

        return (
            f"Page {self.pagination.current_page} of {self.pagination.total_pages} "
            f"(items {start_item}-{end_item} of {self.pagination.total_items})"
        )
