"""Unified recommendations client."""

from client.recommendations.movies import MovieRecommendationsClient
from client.recommendations.shows import ShowRecommendationsClient


class RecommendationsClient(MovieRecommendationsClient, ShowRecommendationsClient):
    """Unified client for all recommendation operations.

    Combines functionality from:
    - MovieRecommendationsClient: get_movie_recommendations(), hide_movie_recommendation()
    - ShowRecommendationsClient: get_show_recommendations(), hide_show_recommendation()

    Note: Inherits OAuth authentication handling from AuthClient through parent clients.
    All recommendation operations require user authentication to access personalized data.
    """

    pass
