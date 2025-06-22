"""Movies module for the Trakt MCP server."""

from .resources import register_movie_resources
from .tools import register_movie_tools

__all__ = ["register_movie_resources", "register_movie_tools"]
