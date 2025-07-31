# pyright: reportUnusedFunction=none
"""Comment tools for the Trakt MCP server."""

from mcp.server.fastmcp import FastMCP

from client.comments import CommentsClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.comments import CommentsFormatters


async def fetch_movie_comments(
    movie_id: str,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: str = "newest",
) -> str:
    """Fetch comments for a movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about movie comments
    """
    client = CommentsClient()
    comments = await client.get_movie_comments(movie_id, limit=limit, sort=sort)
    title = f"Movie ID: {movie_id}"
    return CommentsFormatters.format_comments(
        comments, title, show_spoilers=show_spoilers
    )


async def fetch_show_comments(
    show_id: str,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: str = "newest",
) -> str:
    """Fetch comments for a show from Trakt.

    Args:
        show_id: Trakt ID of the show
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about show comments
    """
    client = CommentsClient()
    comments = await client.get_show_comments(show_id, limit=limit, sort=sort)
    title = f"Show ID: {show_id}"
    return CommentsFormatters.format_comments(
        comments, title, show_spoilers=show_spoilers
    )


async def fetch_season_comments(
    show_id: str,
    season: int,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: str = "newest",
) -> str:
    """Fetch comments for a season from Trakt.

    Args:
        show_id: Trakt ID of the show
        season: Season number
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about season comments
    """
    client = CommentsClient()
    comments = await client.get_season_comments(show_id, season, limit=limit, sort=sort)
    title = f"Show ID: {show_id} - Season {season}"
    return CommentsFormatters.format_comments(
        comments, title, show_spoilers=show_spoilers
    )


async def fetch_episode_comments(
    show_id: str,
    season: int,
    episode: int,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: str = "newest",
) -> str:
    """Fetch comments for an episode from Trakt.

    Args:
        show_id: Trakt ID of the show
        season: Season number
        episode: Episode number
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about episode comments
    """
    client = CommentsClient()
    comments = await client.get_episode_comments(
        show_id, season, episode, limit=limit, sort=sort
    )
    title = f"Show ID: {show_id} - S{season:02d}E{episode:02d}"
    return CommentsFormatters.format_comments(
        comments, title, show_spoilers=show_spoilers
    )


async def fetch_comment(comment_id: str, show_spoilers: bool = False) -> str:
    """Fetch a specific comment from Trakt.

    Args:
        comment_id: Trakt ID of the comment
        show_spoilers: Whether to show spoilers by default

    Returns:
        Information about the comment
    """
    client = CommentsClient()
    comment = await client.get_comment(comment_id)
    return CommentsFormatters.format_comment(comment, show_spoilers=show_spoilers)


async def fetch_comment_replies(
    comment_id: str,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: str = "newest",
) -> str:
    """Fetch replies for a comment from Trakt.

    Args:
        comment_id: Trakt ID of the comment
        limit: Maximum number of replies to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort replies (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about the comment and its replies
    """
    client = CommentsClient()
    comment = await client.get_comment(comment_id)
    replies = await client.get_comment_replies(comment_id, limit=limit, sort=sort)
    return CommentsFormatters.format_comment(
        comment, with_replies=True, replies=replies, show_spoilers=show_spoilers
    )


def register_comment_tools(mcp: FastMCP) -> None:
    """Register comment tools with the MCP server."""

    @mcp.tool(
        name=TOOL_NAMES["fetch_movie_comments"],
        description="Fetch comments for a specific movie from Trakt",
    )
    async def fetch_movie_comments_tool(
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        show_spoilers: bool = False,
        sort: str = "newest",
    ) -> str:
        return await fetch_movie_comments(movie_id, limit, show_spoilers, sort)

    @mcp.tool(
        name=TOOL_NAMES["fetch_show_comments"],
        description="Fetch comments for a specific TV show from Trakt",
    )
    async def fetch_show_comments_tool(
        show_id: str,
        limit: int = DEFAULT_LIMIT,
        show_spoilers: bool = False,
        sort: str = "newest",
    ) -> str:
        return await fetch_show_comments(show_id, limit, show_spoilers, sort)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_comments"],
        description="Fetch comments for a specific TV show season from Trakt",
    )
    async def fetch_season_comments_tool(
        show_id: str,
        season: int,
        limit: int = DEFAULT_LIMIT,
        show_spoilers: bool = False,
        sort: str = "newest",
    ) -> str:
        return await fetch_season_comments(show_id, season, limit, show_spoilers, sort)

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_comments"],
        description="Fetch comments for a specific TV show episode from Trakt",
    )
    async def fetch_episode_comments_tool(
        show_id: str,
        season: int,
        episode: int,
        limit: int = DEFAULT_LIMIT,
        show_spoilers: bool = False,
        sort: str = "newest",
    ) -> str:
        return await fetch_episode_comments(
            show_id, season, episode, limit, show_spoilers, sort
        )

    @mcp.tool(
        name=TOOL_NAMES["fetch_comment"],
        description="Fetch a specific comment from Trakt",
    )
    async def fetch_comment_tool(comment_id: str, show_spoilers: bool = False) -> str:
        return await fetch_comment(comment_id, show_spoilers)

    @mcp.tool(
        name=TOOL_NAMES["fetch_comment_replies"],
        description="Fetch replies for a specific comment from Trakt",
    )
    async def fetch_comment_replies_tool(
        comment_id: str,
        limit: int = DEFAULT_LIMIT,
        show_spoilers: bool = False,
        sort: str = "newest",
    ) -> str:
        return await fetch_comment_replies(comment_id, limit, show_spoilers, sort)
