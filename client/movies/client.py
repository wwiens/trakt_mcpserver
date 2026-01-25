"""Unified movies client that combines all movie functionality."""

from .details import MovieDetailsClient
from .popular import PopularMoviesClient
from .related import RelatedMoviesClient
from .stats import MovieStatsClient
from .trending import TrendingMoviesClient
from .videos import MovieVideosClient


class MoviesClient(
    TrendingMoviesClient,
    PopularMoviesClient,
    MovieStatsClient,
    MovieDetailsClient,
    MovieVideosClient,
    RelatedMoviesClient,
):
    """Unified client for all movie-related operations.

    Combines functionality from:
    - TrendingMoviesClient: get_trending_movies()
    - PopularMoviesClient: get_popular_movies()
    - MovieStatsClient: get_favorited_movies(), get_played_movies(), get_watched_movies()
    - MovieDetailsClient: get_movie(), get_movie_ratings()
    - MovieVideosClient: get_videos()
    - RelatedMoviesClient: get_related_movies()
    """

    pass
