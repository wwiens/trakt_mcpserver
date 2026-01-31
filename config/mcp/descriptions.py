"""Common descriptions for MCP tool parameters.

This module centralizes frequently-used parameter descriptions to ensure
consistency across tools and reduce duplication.

Naming Convention:
    All constants use the suffix `_DESCRIPTION` and are named after the
    parameter they describe in SCREAMING_SNAKE_CASE.

    Examples:
        - MOVIE_ID_DESCRIPTION for movie_id parameters
        - PAGE_DESCRIPTION for page parameters
        - LIMIT_DESCRIPTION for limit parameters
"""

from typing import Final

from config.api.constants import DEFAULT_FETCH_ALL_LIMIT, DEFAULT_LIMIT

__all__ = [
    "COMMENTS_LIMIT_DESCRIPTION",
    "COMMENT_ID_DESCRIPTION",
    "COMMENT_SORT_DESCRIPTION",
    "EMBED_MARKDOWN_DESCRIPTION",
    "EPISODE_DESCRIPTION",
    "EXTENDED_DESCRIPTION",
    "HISTORY_END_AT_DESCRIPTION",
    "HISTORY_ITEMS_DESCRIPTION",
    "HISTORY_ITEM_ID_DESCRIPTION",
    "HISTORY_QUERY_TYPE_DESCRIPTION",
    "HISTORY_REMOVE_ITEMS_DESCRIPTION",
    "HISTORY_START_AT_DESCRIPTION",
    "HISTORY_TYPE_DESCRIPTION",
    "IGNORE_COLLECTED_DESCRIPTION",
    "IGNORE_WATCHLISTED_DESCRIPTION",
    "LIMIT_DESCRIPTION",
    "MAX_PAGES_DESCRIPTION",
    "MOVIE_ID_DESCRIPTION",
    "PAGE_DESCRIPTION",
    "PERIOD_DESCRIPTION",
    "PLAYBACK_ID_DESCRIPTION",
    "PLAYBACK_TYPE_DESCRIPTION",
    "RATING_FILTER_DESCRIPTION",
    "RATING_ITEMS_DESCRIPTION",
    "RATING_REMOVE_ITEMS_DESCRIPTION",
    "RATING_TYPE_DESCRIPTION",
    "RECOMMENDATIONS_LIMIT_DESCRIPTION",
    "REPLIES_LIMIT_DESCRIPTION",
    "SEARCH_LIMIT_DESCRIPTION",
    "SEARCH_QUERY_DESCRIPTION",
    "SEASON_DESCRIPTION",
    "SHOW_ID_DESCRIPTION",
    "SHOW_PROGRESS_COUNT_SPECIALS_DESCRIPTION",
    "SHOW_PROGRESS_HIDDEN_DESCRIPTION",
    "SHOW_PROGRESS_LAST_ACTIVITY_DESCRIPTION",
    "SHOW_PROGRESS_SPECIALS_DESCRIPTION",
    "SHOW_PROGRESS_VERBOSE_DESCRIPTION",
    "SHOW_SPOILERS_DESCRIPTION",
    "SORT_DIRECTION_DESCRIPTION",
    "USER_LIMIT_DESCRIPTION",
    "WATCHLIST_ITEMS_DESCRIPTION",
    "WATCHLIST_REMOVE_ITEMS_DESCRIPTION",
    "WATCHLIST_SORT_BY_DESCRIPTION",
    "WATCHLIST_TYPE_DESCRIPTION",
    "WATCHLIST_TYPE_REQUIRED_DESCRIPTION",
]

# ID parameter descriptions with examples
SHOW_ID_DESCRIPTION: Final[str] = (
    "Trakt ID, Trakt slug, or IMDB ID (e.g., '1388', 'breaking-bad', 'tt0903747')"
)
MOVIE_ID_DESCRIPTION: Final[str] = (
    "Trakt ID, Trakt slug, or IMDB ID "
    "(e.g., '120', 'the-dark-knight-2008', 'tt0468569')"
)
COMMENT_ID_DESCRIPTION: Final[str] = (
    "Trakt comment ID (numeric string, e.g., '417', '12345')"
)

# Pagination descriptions
PAGE_DESCRIPTION: Final[str] = "Page number (omit to auto-paginate)"
MAX_PAGES_DESCRIPTION: Final[str] = "Maximum pages to fetch during auto-pagination"
LIMIT_DESCRIPTION: Final[str] = (
    f"Number of results to return (default {DEFAULT_LIMIT}, "
    f"0=up to {DEFAULT_FETCH_ALL_LIMIT} when page omitted)"
)

# Specific limit descriptions for different contexts
COMMENTS_LIMIT_DESCRIPTION: Final[str] = (
    f"Number of comments to return (default {DEFAULT_LIMIT}, "
    f"0=up to {DEFAULT_FETCH_ALL_LIMIT} when page omitted)"
)
REPLIES_LIMIT_DESCRIPTION: Final[str] = (
    f"Number of replies to return (default {DEFAULT_LIMIT}, "
    f"0=up to {DEFAULT_FETCH_ALL_LIMIT} when page omitted)"
)
SEARCH_LIMIT_DESCRIPTION: Final[str] = (
    f"Maximum results to return (default {DEFAULT_LIMIT}, "
    f"0=up to {DEFAULT_FETCH_ALL_LIMIT} when page omitted)"
)
USER_LIMIT_DESCRIPTION: Final[str] = (
    f"Maximum number of items to return (0=up to {DEFAULT_FETCH_ALL_LIMIT}, default). "
    "None is treated as 0."
)
RECOMMENDATIONS_LIMIT_DESCRIPTION: Final[str] = (
    f"Number of recommendations to return (1-{DEFAULT_FETCH_ALL_LIMIT}, "
    f"default {DEFAULT_LIMIT})"
)

# Period descriptions
PERIOD_DESCRIPTION: Final[str] = (
    "Time period: 'daily', 'weekly' (default), 'monthly', 'yearly', or 'all' (all-time)"
)

# Sort descriptions
COMMENT_SORT_DESCRIPTION: Final[str] = (
    "Sort order: 'newest', 'oldest', 'likes' (most liked), or 'replies' (most replies)"
)
WATCHLIST_SORT_BY_DESCRIPTION: Final[str] = (
    "Field to sort by: 'rank' (default), 'added', 'title', 'released', "
    "'runtime', 'popularity', 'percentage', 'votes'"
)
SORT_DIRECTION_DESCRIPTION: Final[str] = (
    "Sort direction: 'asc' (ascending) or 'desc' (descending)"
)

# Spoiler descriptions
SHOW_SPOILERS_DESCRIPTION: Final[str] = (
    "Include spoiler-tagged comments in output (default: hidden)"
)

# Season/Episode descriptions
SEASON_DESCRIPTION: Final[str] = "Season number (e.g., 1, 2, 3)"
EPISODE_DESCRIPTION: Final[str] = "Episode number (e.g., 1, 2, 3)"

# Search descriptions
SEARCH_QUERY_DESCRIPTION: Final[str] = (
    "Search query text to match against title, overview, and other text fields"
)

# Extended info descriptions
EXTENDED_DESCRIPTION: Final[str] = (
    "Return comprehensive data (True) or only title/year/IDs (False)"
)

# Embed markdown descriptions
EMBED_MARKDOWN_DESCRIPTION: Final[str] = (
    "Use embedded YouTube iframe markdown (True) or simple links (False)"
)

# Recommendations filter descriptions
IGNORE_COLLECTED_DESCRIPTION: Final[str] = (
    "Filter out items the user has already collected"
)
IGNORE_WATCHLISTED_DESCRIPTION: Final[str] = (
    "Filter out items the user has already watchlisted"
)

# Content type descriptions
RATING_TYPE_DESCRIPTION: Final[str] = (
    "Type of content: 'movies', 'shows', 'seasons', or 'episodes'"
)
WATCHLIST_TYPE_DESCRIPTION: Final[str] = (
    "Type of content: 'all' (default), 'movies', 'shows', 'seasons', or 'episodes'"
)
WATCHLIST_TYPE_REQUIRED_DESCRIPTION: Final[str] = (
    "Type of content: 'movies', 'shows', 'seasons', or 'episodes'"
)

# Rating-specific descriptions
RATING_FILTER_DESCRIPTION: Final[str] = "Filter by specific rating (1-10)"

# Items list descriptions
RATING_ITEMS_DESCRIPTION: Final[str] = (
    "List of items to rate. Each item must include a 'rating' (1-10) "
    "and either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'"
)
RATING_REMOVE_ITEMS_DESCRIPTION: Final[str] = (
    "List of items to remove ratings from. Each item must include "
    "either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'"
)
WATCHLIST_ITEMS_DESCRIPTION: Final[str] = (
    "List of items to add to watchlist. Each item must include "
    "either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'. Optional 'notes' field (VIP only, 500 char max)"
)
WATCHLIST_REMOVE_ITEMS_DESCRIPTION: Final[str] = (
    "List of items to remove from watchlist. Each item must include "
    "either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'"
)

# Progress descriptions
SHOW_PROGRESS_HIDDEN_DESCRIPTION: Final[str] = (
    "Include hidden seasons in progress calculation (default: false)"
)
SHOW_PROGRESS_SPECIALS_DESCRIPTION: Final[str] = (
    "Include specials as season 0 in progress (default: false)"
)
SHOW_PROGRESS_COUNT_SPECIALS_DESCRIPTION: Final[str] = (
    "Count specials in overall stats when specials are included (default: true)"
)
SHOW_PROGRESS_LAST_ACTIVITY_DESCRIPTION: Final[str] = (
    "Calculate last/next episode based on: 'aired' (default) or 'watched'"
)
SHOW_PROGRESS_VERBOSE_DESCRIPTION: Final[str] = (
    "Show episode-by-episode watch dates within each season (default: false)"
)
PLAYBACK_TYPE_DESCRIPTION: Final[str] = (
    "Type of playback progress: 'movies', 'episodes', or omit for all"
)
PLAYBACK_ID_DESCRIPTION: Final[str] = (
    "Playback item ID to remove (from fetch_playback_progress results)"
)
HISTORY_TYPE_DESCRIPTION: Final[str] = (
    "Type of content: 'movies', 'shows', 'seasons', or 'episodes'"
)
HISTORY_QUERY_TYPE_DESCRIPTION: Final[str] = (
    "Content type to filter history: 'movies', 'shows', 'seasons', or 'episodes'. "
    "Required when querying a specific item."
)
HISTORY_ITEM_ID_DESCRIPTION: Final[str] = (
    "Trakt ID (numeric) of the specific item to check. "
    "Examples: '1388', '5106'. "
    "Requires history_type to be specified."
)
HISTORY_START_AT_DESCRIPTION: Final[str] = (
    "Filter watches after this date (ISO 8601, e.g., '2024-01-01T00:00:00.000Z')"
)
HISTORY_END_AT_DESCRIPTION: Final[str] = (
    "Filter watches before this date (ISO 8601, e.g., '2024-12-31T23:59:59.000Z')"
)
HISTORY_ITEMS_DESCRIPTION: Final[str] = (
    "List of items to add to history. Each item must include "
    "either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'. Optional 'watched_at' (ISO 8601 timestamp)"
)
HISTORY_REMOVE_ITEMS_DESCRIPTION: Final[str] = (
    "List of items to remove from history. Each item must include "
    "either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'"
)
