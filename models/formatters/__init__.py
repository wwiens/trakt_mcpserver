"""Domain-specific formatters for the Trakt MCP server.

This module provides domain-focused formatters for different types of Trakt data:

- models.formatters.auth: Authentication formatting (AuthFormatters)
- models.formatters.checkin: Check-in formatting (CheckinFormatters)
- models.formatters.comments: Comments formatting (CommentsFormatters)
- models.formatters.movies: Movies formatting (MovieFormatters)
- models.formatters.search: Search formatting (SearchFormatters)
- models.formatters.shows: Shows formatting (ShowFormatters)
- models.formatters.user: User data formatting (UserFormatters)

Use direct imports for better clarity:
    from models.formatters.shows import ShowFormatters
    from models.formatters.movies import MovieFormatters
    from models.formatters.auth import AuthFormatters
    # etc.
"""

from .auth import AuthFormatters
from .checkin import CheckinFormatters
from .comments import CommentsFormatters
from .movies import MovieFormatters
from .search import SearchFormatters
from .shows import ShowFormatters
from .user import UserFormatters

__all__ = [
    "AuthFormatters",
    "CheckinFormatters",
    "CommentsFormatters",
    "MovieFormatters",
    "SearchFormatters",
    "ShowFormatters",
    "UserFormatters",
]
