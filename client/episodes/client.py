"""Unified episodes client that combines all episode functionality."""

from .lists import EpisodeListsClient
from .people import EpisodePeopleClient
from .ratings import EpisodeRatingsClient
from .stats import EpisodeStatsClient
from .summary import EpisodeSummaryClient
from .translations import EpisodeTranslationsClient
from .videos import EpisodeVideosClient
from .watching import EpisodeWatchingClient


class EpisodesClient(
    EpisodeSummaryClient,
    EpisodeRatingsClient,
    EpisodeStatsClient,
    EpisodePeopleClient,
    EpisodeVideosClient,
    EpisodeWatchingClient,
    EpisodeTranslationsClient,
    EpisodeListsClient,
):
    """Unified client for all episode-related operations.

    Combines functionality from:
    - EpisodeSummaryClient: get_episode()
    - EpisodeRatingsClient: get_episode_ratings()
    - EpisodeStatsClient: get_episode_stats()
    - EpisodePeopleClient: get_episode_people()
    - EpisodeVideosClient: get_episode_videos()
    - EpisodeWatchingClient: get_episode_watching()
    - EpisodeTranslationsClient: get_episode_translations()
    - EpisodeListsClient: get_episode_lists()
    """

    pass
