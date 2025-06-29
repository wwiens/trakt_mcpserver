"""Shows module for the Trakt MCP server."""

from .resources import register_show_resources
from .tools import register_show_tools

__all__ = ["register_show_resources", "register_show_tools"]
