"""Comments-specific MCP tool name definitions."""

from typing import Final

COMMENT_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_movie_comments",
        "fetch_show_comments",
        "fetch_season_comments",
        "fetch_episode_comments",
        "fetch_comment",
        "fetch_comment_replies",
    }
)
