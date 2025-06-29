"""Model modules for the Trakt MCP server."""

from .auth import TraktAuthToken, TraktDeviceCode
from .movies import TraktMovie, TraktPopularMovie, TraktTrendingMovie
from .shows import TraktEpisode, TraktPopularShow, TraktShow, TraktTrendingShow
from .user import TraktUserShow

__all__ = [
    "TraktAuthToken",
    "TraktDeviceCode",
    "TraktEpisode",
    "TraktMovie",
    "TraktPopularMovie",
    "TraktPopularShow",
    "TraktShow",
    "TraktTrendingMovie",
    "TraktTrendingShow",
    "TraktUserShow",
]
