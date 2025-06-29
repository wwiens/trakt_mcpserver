"""Trakt API endpoints organized by domain."""

from .auth import AUTH_ENDPOINTS
from .checkin import CHECKIN_ENDPOINTS
from .comments import COMMENTS_ENDPOINTS
from .movies import MOVIES_ENDPOINTS
from .search import SEARCH_ENDPOINTS
from .shows import SHOWS_ENDPOINTS
from .user import USER_ENDPOINTS

# Combined endpoints dictionary for backward compatibility
TRAKT_ENDPOINTS = {
    **AUTH_ENDPOINTS,
    **SHOWS_ENDPOINTS,
    **MOVIES_ENDPOINTS,
    **SEARCH_ENDPOINTS,
    **CHECKIN_ENDPOINTS,
    **COMMENTS_ENDPOINTS,
    **USER_ENDPOINTS,
}

__all__ = [
    "AUTH_ENDPOINTS",
    "CHECKIN_ENDPOINTS",
    "COMMENTS_ENDPOINTS",
    "MOVIES_ENDPOINTS",
    "SEARCH_ENDPOINTS",
    "SHOWS_ENDPOINTS",
    "TRAKT_ENDPOINTS",
    "USER_ENDPOINTS",
]
