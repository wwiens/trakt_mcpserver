"""Unified seasons client that combines all season functionality."""

from .episodes import SeasonEpisodesClient
from .info import SeasonInfoClient
from .lists import SeasonListsClient
from .people import SeasonPeopleClient
from .ratings import SeasonRatingsClient
from .stats import SeasonStatsClient
from .translations import SeasonTranslationsClient
from .videos import SeasonVideosClient
from .watching import SeasonWatchingClient


class SeasonsClient(
    SeasonInfoClient,
    SeasonEpisodesClient,
    SeasonRatingsClient,
    SeasonStatsClient,
    SeasonPeopleClient,
    SeasonVideosClient,
    SeasonWatchingClient,
    SeasonTranslationsClient,
    SeasonListsClient,
):
    """Unified client for all season-related operations.

    Combines functionality from:
    - SeasonInfoClient: get_season()
    - SeasonEpisodesClient: get_season_episodes()
    - SeasonRatingsClient: get_season_ratings()
    - SeasonStatsClient: get_season_stats()
    - SeasonPeopleClient: get_season_people()
    - SeasonVideosClient: get_season_videos()
    - SeasonWatchingClient: get_season_watching()
    - SeasonTranslationsClient: get_season_translations()
    - SeasonListsClient: get_season_lists()
    """

    pass
