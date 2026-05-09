"""Common type definitions and utilities."""

from typing import TypedDict

JSONValue = str | int | float | bool | None | dict[str, "JSONValue"] | list["JSONValue"]


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
