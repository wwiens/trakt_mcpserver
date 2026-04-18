"""Type alias listing every valid endpoint key.

Using this ``Literal`` as the key type of ``TRAKT_ENDPOINTS`` causes type
checkers to reject unknown or mistyped keys at subscript sites.
"""

from typing import Literal

EndpointKey = Literal[
    # Auth
    "device_code",
    "device_token",
    "token",
    "revoke",
    # Checkin
    "checkin",
    # Comments
    "comments_movie",
    "comments_show",
    "comments_season",
    "comments_episode",
    "comment",
    "comment_replies",
    # Episodes
    "episode_summary",
    "episode_translations",
    "episode_lists",
    "episode_people",
    "episode_ratings",
    "episode_stats",
    "episode_watching",
    "episode_videos",
    # Movies
    "movies_trending",
    "movies_popular",
    "movies_favorited",
    "movies_played",
    "movies_watched",
    "movies_anticipated",
    "movie_ratings",
    "movie_videos",
    "movies_related",
    "movies_boxoffice",
    "movie_people",
    # People
    "person_summary",
    "person_movies",
    "person_shows",
    "person_lists",
    # Progress
    "show_progress_watched",
    "sync_playback",
    "sync_playback_type",
    "sync_playback_remove",
    # Recommendations
    "recommendations_movies",
    "recommendations_shows",
    "hide_movie_recommendation",
    "hide_show_recommendation",
    "unhide_recommendations",
    # Search
    "search",
    # Seasons
    "season_info",
    "season_episodes",
    "season_ratings",
    "season_stats",
    "season_people",
    "season_videos",
    "season_watching",
    "season_translations",
    "season_lists",
    # Shows
    "shows_trending",
    "shows_popular",
    "shows_favorited",
    "shows_played",
    "shows_watched",
    "shows_anticipated",
    "show_ratings",
    "show_videos",
    "shows_related",
    "show_seasons",
    "show_people",
    # Sync
    "sync_ratings_get",
    "sync_ratings_get_type",
    "sync_ratings_add",
    "sync_ratings_remove",
    "sync_watchlist_add",
    "sync_watchlist_get",
    "sync_watchlist_get_all",
    "sync_watchlist_get_type",
    "sync_watchlist_remove",
    "sync_history_get",
    "sync_history_get_type",
    "sync_history_add",
    "sync_history_remove",
    # User
    "user_watched_shows",
    "user_watched_movies",
]
