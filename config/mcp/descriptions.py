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

__all__ = [
    "COMMENTS_LIMIT_DESCRIPTION",
    "COMMENT_ID_DESCRIPTION",
    "COMMENT_SORT_DESCRIPTION",
    "EMBED_MARKDOWN_DESCRIPTION",
    "EPISODE_DESCRIPTION",
    "EXTENDED_DESCRIPTION",
    "IGNORE_COLLECTED_DESCRIPTION",
    "IGNORE_WATCHLISTED_DESCRIPTION",
    "LIMIT_DESCRIPTION",
    "MAX_PAGES_DESCRIPTION",
    "MOVIE_ID_DESCRIPTION",
    "PAGE_DESCRIPTION",
    "PERIOD_DESCRIPTION",
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
SHOW_ID_DESCRIPTION = (
    "Trakt ID, Trakt slug, or IMDB ID (e.g., '1388', 'breaking-bad', 'tt0903747')"
)
MOVIE_ID_DESCRIPTION = "Trakt ID, Trakt slug, or IMDB ID (e.g., '120', 'the-dark-knight-2008', 'tt0468569')"
COMMENT_ID_DESCRIPTION = "Trakt comment ID (numeric string, e.g., '417', '12345')"

# Pagination descriptions
PAGE_DESCRIPTION = "Page number (omit to fetch all pages)"
MAX_PAGES_DESCRIPTION = "Maximum pages to fetch during auto-pagination"
LIMIT_DESCRIPTION = "Number of results to return (default 10)"

# Specific limit descriptions for different contexts
COMMENTS_LIMIT_DESCRIPTION = "Number of comments to return (default 10)"
REPLIES_LIMIT_DESCRIPTION = "Number of replies to return (default 10)"
SEARCH_LIMIT_DESCRIPTION = "Maximum results to return (0=all, default 10)"
USER_LIMIT_DESCRIPTION = (
    "Maximum number of items to return. Use 0 to return all items (default). Max 100. "
    "None is treated as 0."
)
RECOMMENDATIONS_LIMIT_DESCRIPTION = (
    "Number of recommendations to return (1-100, default 10)"
)

# Period descriptions
PERIOD_DESCRIPTION = (
    "Time period: 'daily', 'weekly' (default), 'monthly', 'yearly', or 'all' (all-time)"
)

# Sort descriptions
COMMENT_SORT_DESCRIPTION = (
    "Sort order: 'newest', 'oldest', 'likes' (most liked), or 'replies' (most replies)"
)
WATCHLIST_SORT_BY_DESCRIPTION = (
    "Field to sort by: 'rank' (default), 'added', 'title', 'released', "
    "'runtime', 'popularity', 'percentage', 'votes'"
)
SORT_DIRECTION_DESCRIPTION = "Sort direction: 'asc' (ascending) or 'desc' (descending)"

# Spoiler descriptions
SHOW_SPOILERS_DESCRIPTION = (
    "Include spoiler-tagged comments in output (default: hidden)"
)

# Season/Episode descriptions
SEASON_DESCRIPTION = "Season number (e.g., 1, 2, 3)"
EPISODE_DESCRIPTION = "Episode number (e.g., 1, 2, 3)"

# Search descriptions
SEARCH_QUERY_DESCRIPTION = (
    "Search query text to match against title, overview, and other text fields"
)

# Extended info descriptions
EXTENDED_DESCRIPTION = "Return comprehensive data (True) or only title/year/IDs (False)"

# Embed markdown descriptions
EMBED_MARKDOWN_DESCRIPTION = (
    "Use embedded YouTube iframe markdown (True) or simple links (False)"
)

# Recommendations filter descriptions
IGNORE_COLLECTED_DESCRIPTION = "Filter out items the user has already collected"
IGNORE_WATCHLISTED_DESCRIPTION = "Filter out items the user has already watchlisted"

# Content type descriptions
RATING_TYPE_DESCRIPTION = "Type of content: 'movies', 'shows', 'seasons', or 'episodes'"
WATCHLIST_TYPE_DESCRIPTION = (
    "Type of content: 'all' (default), 'movies', 'shows', 'seasons', or 'episodes'"
)
WATCHLIST_TYPE_REQUIRED_DESCRIPTION = (
    "Type of content: 'movies', 'shows', 'seasons', or 'episodes'"
)

# Rating-specific descriptions
RATING_FILTER_DESCRIPTION = "Filter by specific rating (1-10)"

# Items list descriptions
RATING_ITEMS_DESCRIPTION = (
    "List of items to rate. Each item must include a 'rating' (1-10) "
    "and either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'"
)
RATING_REMOVE_ITEMS_DESCRIPTION = (
    "List of items to remove ratings from. Each item must include "
    "either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'"
)
WATCHLIST_ITEMS_DESCRIPTION = (
    "List of items to add to watchlist. Each item must include "
    "either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'. Optional 'notes' field (VIP only, 500 char max)"
)
WATCHLIST_REMOVE_ITEMS_DESCRIPTION = (
    "List of items to remove from watchlist. Each item must include "
    "either an identifier (trakt_id, slug, imdb_id, tmdb_id, tvdb_id) "
    "or both 'title' and 'year'"
)
