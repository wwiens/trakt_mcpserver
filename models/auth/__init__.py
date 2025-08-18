"""Authentication models for the Trakt MCP server."""

from .auth import DeviceTokenRequest, TraktAuthToken, TraktDeviceCode

__all__ = ["DeviceTokenRequest", "TraktAuthToken", "TraktDeviceCode"]
