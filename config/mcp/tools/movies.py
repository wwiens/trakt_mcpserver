"""Movie-specific MCP tool name definitions."""

from typing import Final

MOVIE_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_trending_movies",
        "fetch_popular_movies",
        "fetch_favorited_movies",
        "fetch_played_movies",
        "fetch_watched_movies",
        "fetch_anticipated_movies",
        "fetch_movie_ratings",
        "fetch_movie_summary",
        "fetch_movie_videos",
        "fetch_related_movies",
        "fetch_boxoffice_movies",
        "fetch_movie_people",
    }
)
