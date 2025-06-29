"""Authentication models for the Trakt MCP server."""

from .auth import TraktAuthToken, TraktDeviceCode

__all__ = ["TraktAuthToken", "TraktDeviceCode"]
