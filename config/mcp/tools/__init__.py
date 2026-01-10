"""MCP tools organized by domain."""

from .auth import AUTH_TOOLS
from .checkin import CHECKIN_TOOLS
from .comments import COMMENT_TOOLS
from .movies import MOVIE_TOOLS
from .recommendations import RECOMMENDATIONS_TOOLS
from .search import SEARCH_TOOLS
from .shows import SHOW_TOOLS
from .sync import SYNC_TOOLS
from .user import USER_TOOLS

# Combine all tools for backward compatibility
TOOL_NAMES = {
    **SHOW_TOOLS,
    **MOVIE_TOOLS,
    **AUTH_TOOLS,
    **USER_TOOLS,
    **CHECKIN_TOOLS,
    **COMMENT_TOOLS,
    **RECOMMENDATIONS_TOOLS,
    **SEARCH_TOOLS,
    **SYNC_TOOLS,
}

__all__ = [
    "AUTH_TOOLS",
    "CHECKIN_TOOLS",
    "COMMENT_TOOLS",
    "MOVIE_TOOLS",
    "RECOMMENDATIONS_TOOLS",
    "SEARCH_TOOLS",
    "SHOW_TOOLS",
    "SYNC_TOOLS",
    "TOOL_NAMES",
    "USER_TOOLS",
]
