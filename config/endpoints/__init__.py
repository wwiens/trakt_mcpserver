"""Trakt API endpoints organized by domain."""

from typing import Final

from .auth import AUTH_ENDPOINTS
from .checkin import CHECKIN_ENDPOINTS
from .comments import COMMENTS_ENDPOINTS
from .episodes import EPISODES_ENDPOINTS
from .movies import MOVIES_ENDPOINTS
from .people import PEOPLE_ENDPOINTS
from .progress import PROGRESS_ENDPOINTS
from .recommendations import RECOMMENDATIONS_ENDPOINTS
from .search import SEARCH_ENDPOINTS
from .seasons import SEASONS_ENDPOINTS
from .shows import SHOWS_ENDPOINTS
from .user import USER_ENDPOINTS

# Combined endpoints dictionary for backward compatibility
TRAKT_ENDPOINTS: Final[dict[str, str]] = {
    **AUTH_ENDPOINTS,
    **SHOWS_ENDPOINTS,
    **MOVIES_ENDPOINTS,
    **PEOPLE_ENDPOINTS,
    **PROGRESS_ENDPOINTS,
    **RECOMMENDATIONS_ENDPOINTS,
    **SEARCH_ENDPOINTS,
    **CHECKIN_ENDPOINTS,
    **COMMENTS_ENDPOINTS,
    **EPISODES_ENDPOINTS,
    **SEASONS_ENDPOINTS,
    **USER_ENDPOINTS,
}

__all__ = [
    "AUTH_ENDPOINTS",
    "CHECKIN_ENDPOINTS",
    "COMMENTS_ENDPOINTS",
    "EPISODES_ENDPOINTS",
    "MOVIES_ENDPOINTS",
    "PEOPLE_ENDPOINTS",
    "PROGRESS_ENDPOINTS",
    "RECOMMENDATIONS_ENDPOINTS",
    "SEARCH_ENDPOINTS",
    "SEASONS_ENDPOINTS",
    "SHOWS_ENDPOINTS",
    "TRAKT_ENDPOINTS",
    "USER_ENDPOINTS",
]
