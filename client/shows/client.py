"""Unified shows client that combines all show functionality."""

from .details import ShowDetailsClient
from .popular import PopularShowsClient
from .stats import ShowStatsClient
from .trending import TrendingShowsClient
from .videos import ShowVideosClient


class ShowsClient(
    TrendingShowsClient,
    PopularShowsClient,
    ShowStatsClient,
    ShowDetailsClient,
    ShowVideosClient,
):
    """Unified client for all show-related operations.

    Combines functionality from:
    - TrendingShowsClient: get_trending_shows()
    - PopularShowsClient: get_popular_shows()
    - ShowStatsClient: get_favorited_shows(), get_played_shows(), get_watched_shows()
    - ShowDetailsClient: get_show(), get_show_ratings()
    - ShowVideosClient: get_videos()
    """

    pass
