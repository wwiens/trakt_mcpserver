"""Common type definitions and utilities."""

from typing import TypedDict, TypeVar

# Generic type variables
T = TypeVar("T")
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


# Common response types
class ErrorResponse(TypedDict):
    """API error response."""

    error: str
    error_description: str


# Headers type
TraktHeaders = TypedDict(
    "TraktHeaders",
    {
        "Authorization": str,
        "trakt_api_version": str,
        "trakt_api_key": str,
        "Content-Type": str,
    },
    total=False,
)
