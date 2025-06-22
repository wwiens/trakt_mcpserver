"""Authentication module for the Trakt MCP server."""

from .resources import register_auth_resources
from .tools import register_auth_tools

__all__ = ["register_auth_resources", "register_auth_tools"]
