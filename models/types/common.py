"""Common type definitions and utilities."""

from typing import Generic, TypedDict, TypeVar

# Generic type variables
T = TypeVar("T")
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


# Common response wrappers
class PaginatedResponse(TypedDict, Generic[T]):
    """Paginated API response."""

    page: int
    limit: int
    pages: int
    total: int
    results: list[T]


class ErrorResponse(TypedDict):
    """API error response."""

    error: str
    error_description: str


# Headers type
class TraktHeaders(TypedDict, total=False):
    """Trakt API headers."""

    Authorization: str
    trakt_api_version: str
    trakt_api_key: str
    Content_Type: str
