"""MCP tools organized by domain."""

from typing import Final

from .auth import AUTH_TOOLS
from .checkin import CHECKIN_TOOLS
from .comments import COMMENT_TOOLS
from .episodes import EPISODE_TOOLS
from .movies import MOVIE_TOOLS
from .people import PEOPLE_TOOLS
from .progress import PROGRESS_TOOLS
from .recommendations import RECOMMENDATIONS_TOOLS
from .search import SEARCH_TOOLS
from .seasons import SEASON_TOOLS
from .shows import SHOW_TOOLS
from .sync import SYNC_TOOLS
from .user import USER_TOOLS

TOOL_NAMES: Final[frozenset[str]] = (
    SHOW_TOOLS
    | MOVIE_TOOLS
    | PEOPLE_TOOLS
    | AUTH_TOOLS
    | USER_TOOLS
    | CHECKIN_TOOLS
    | COMMENT_TOOLS
    | EPISODE_TOOLS
    | PROGRESS_TOOLS
    | RECOMMENDATIONS_TOOLS
    | SEARCH_TOOLS
    | SEASON_TOOLS
    | SYNC_TOOLS
)

__all__ = [
    "AUTH_TOOLS",
    "CHECKIN_TOOLS",
    "COMMENT_TOOLS",
    "EPISODE_TOOLS",
    "MOVIE_TOOLS",
    "PEOPLE_TOOLS",
    "PROGRESS_TOOLS",
    "RECOMMENDATIONS_TOOLS",
    "SEARCH_TOOLS",
    "SEASON_TOOLS",
    "SHOW_TOOLS",
    "SYNC_TOOLS",
    "TOOL_NAMES",
    "USER_TOOLS",
]
