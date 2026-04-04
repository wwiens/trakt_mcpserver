"""Unified movies client that combines all movie functionality."""

from .anticipated import AnticipatedMoviesClient
from .boxoffice import BoxOfficeMoviesClient
from .details import MovieDetailsClient
from .people import MoviePeopleClient
from .popular import PopularMoviesClient
from .related import RelatedMoviesClient
from .stats import MovieStatsClient
from .trending import TrendingMoviesClient
from .videos import MovieVideosClient


class MoviesClient(
    TrendingMoviesClient,
    PopularMoviesClient,
    AnticipatedMoviesClient,
    BoxOfficeMoviesClient,
    MovieStatsClient,
    MovieDetailsClient,
    MovieVideosClient,
    RelatedMoviesClient,
    MoviePeopleClient,
):
    """Unified client for all movie-related operations.

    Combines functionality from:
    - TrendingMoviesClient: get_trending_movies()
    - PopularMoviesClient: get_popular_movies()
    - AnticipatedMoviesClient: get_anticipated_movies()
    - BoxOfficeMoviesClient: get_boxoffice_movies()
    - MovieStatsClient: get_favorited_movies(), get_played_movies(),
      get_watched_movies()
    - MovieDetailsClient: get_movie(), get_movie_ratings()
    - MovieVideosClient: get_videos()
    - RelatedMoviesClient: get_related_movies()
    - MoviePeopleClient: get_movie_people()
    """

    pass
