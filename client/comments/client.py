"""Unified comments client that combines all comment functionality."""

from .details import CommentDetailsClient
from .episode import EpisodeCommentsClient
from .movie import MovieCommentsClient
from .season import SeasonCommentsClient
from .show import ShowCommentsClient


class CommentsClient(
    MovieCommentsClient,
    ShowCommentsClient,
    SeasonCommentsClient,
    EpisodeCommentsClient,
    CommentDetailsClient,
):
    """Unified client for all comment-related operations.

    Combines functionality from:
    - MovieCommentsClient: get_movie_comments()
    - ShowCommentsClient: get_show_comments()
    - SeasonCommentsClient: get_season_comments()
    - EpisodeCommentsClient: get_episode_comments()
    - CommentDetailsClient: get_comment(), get_comment_replies()
    """

    pass
