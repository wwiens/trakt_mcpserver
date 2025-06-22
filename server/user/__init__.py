"""User module for the Trakt MCP server."""

from .resources import register_user_resources
from .tools import register_user_tools

__all__ = ["register_user_resources", "register_user_tools"]
