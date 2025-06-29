"""MCP resources organized by domain."""

from .movies import MOVIE_RESOURCES
from .shows import SHOW_RESOURCES
from .user import USER_RESOURCES

# Combine all resources for backward compatibility
MCP_RESOURCES = {
    **SHOW_RESOURCES,
    **MOVIE_RESOURCES,
    **USER_RESOURCES,
}

__all__ = ["MCP_RESOURCES", "MOVIE_RESOURCES", "SHOW_RESOURCES", "USER_RESOURCES"]
