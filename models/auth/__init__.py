"""Authentication models for the Trakt MCP server."""

from .auth import (
    DeviceTokenRequest,
    OAuthErrorResponse,
    TraktAuthToken,
    TraktDeviceCode,
)

__all__ = [
    "DeviceTokenRequest",
    "OAuthErrorResponse",
    "TraktAuthToken",
    "TraktDeviceCode",
]
