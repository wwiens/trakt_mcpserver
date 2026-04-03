"""Unified shows client that combines all show functionality."""

from .anticipated import AnticipatedShowsClient
from .details import ShowDetailsClient
from .people import ShowPeopleClient
from .popular import PopularShowsClient
from .related import RelatedShowsClient
from .seasons import ShowSeasonsClient
from .stats import ShowStatsClient
from .trending import TrendingShowsClient
from .videos import ShowVideosClient


class ShowsClient(
    TrendingShowsClient,
    PopularShowsClient,
    AnticipatedShowsClient,
    ShowStatsClient,
    ShowDetailsClient,
    ShowVideosClient,
    RelatedShowsClient,
    ShowSeasonsClient,
    ShowPeopleClient,
):
    """Unified client for all show-related operations.

    Combines functionality from:
    - TrendingShowsClient: get_trending_shows()
    - PopularShowsClient: get_popular_shows()
    - AnticipatedShowsClient: get_anticipated_shows()
    - ShowStatsClient: get_favorited_shows(), get_played_shows(), get_watched_shows()
    - ShowDetailsClient: get_show(), get_show_ratings()
    - ShowVideosClient: get_videos()
    - RelatedShowsClient: get_related_shows()
    - ShowSeasonsClient: get_seasons()
    - ShowPeopleClient: get_show_people()
    """

    pass
