"""Comment tools for the Trakt MCP server."""

from collections.abc import Awaitable, Callable
from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, PositiveInt, field_validator

from client.comments.details import CommentDetailsClient
from client.comments.episode import EpisodeCommentsClient
from client.comments.movie import MovieCommentsClient
from client.comments.season import SeasonCommentsClient
from client.comments.show import ShowCommentsClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.comments import CommentsFormatters
from server.base import BaseToolErrorMixin
from server.movies.tools import MovieIdParam
from server.shows.tools import ShowIdParam
from utils.api.errors import handle_api_errors_func

# Comment sort options supported by Trakt API
CommentSort = Literal["newest", "oldest", "likes", "replies"]


class CommentIdParam(BaseModel):
    """Parameters for tools that require a comment ID."""

    comment_id: str = Field(..., min_length=1, description="Non-empty Trakt comment ID")

    @field_validator("comment_id", mode="before")
    @classmethod
    def _strip_comment_id(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


class SeasonParam(BaseModel):
    """Parameters for tools that require show ID and season."""

    show_id: str = Field(..., min_length=1, description="Non-empty Trakt show ID")
    season: PositiveInt = Field(..., description="Season number (positive integer)")

    @field_validator("show_id", mode="before")
    @classmethod
    def _strip_show_id(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


class EpisodeParam(BaseModel):
    """Parameters for tools that require show ID, season, and episode."""

    show_id: str = Field(..., min_length=1, description="Non-empty Trakt show ID")
    season: PositiveInt = Field(..., description="Season number (positive integer)")
    episode: PositiveInt = Field(..., description="Episode number (positive integer)")

    @field_validator("show_id", mode="before")
    @classmethod
    def _strip_show_id(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


# Type aliases for tool functions
MovieCommentsToolType = Callable[[str, int, bool, CommentSort], Awaitable[str]]
ShowCommentsToolType = Callable[[str, int, bool, CommentSort], Awaitable[str]]
SeasonCommentsToolType = Callable[[str, int, int, bool, CommentSort], Awaitable[str]]
EpisodeCommentsToolType = Callable[
    [str, int, int, int, bool, CommentSort], Awaitable[str]
]
CommentToolType = Callable[[str, bool], Awaitable[str]]
CommentRepliesToolType = Callable[[str, int, bool, CommentSort], Awaitable[str]]


@handle_api_errors_func
async def fetch_movie_comments(
    movie_id: str,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: CommentSort = "newest",
) -> str:
    """Fetch comments for a movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies)

    Returns:
        Information about movie comments

    Raises:
        InvalidParamsError: If movie_id is invalid
        InternalError: If an error occurs fetching comments
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = MovieIdParam(movie_id=movie_id)
    movie_id = params.movie_id

    client = MovieCommentsClient()

    comments = await client.get_movie_comments(movie_id, limit=limit, sort=sort)

    # Handle transitional case where API returns error strings
    if isinstance(comments, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="movie_comments",
            resource_id=movie_id,
            error_message=comments,
            operation="fetch_movie_comments",
        )

    title = f"Movie ID: {movie_id}"
    return CommentsFormatters.format_comments(
        comments,
        title,
        show_spoilers=show_spoilers,
    )


@handle_api_errors_func
async def fetch_show_comments(
    show_id: str,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: CommentSort = "newest",
) -> str:
    """Fetch comments for a show from Trakt.

    Args:
        show_id: Trakt ID of the show
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies)

    Returns:
        Information about show comments

    Raises:
        InvalidParamsError: If show_id is invalid
        InternalError: If an error occurs fetching comments
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = ShowIdParam(show_id=show_id)
    show_id = params.show_id

    client = ShowCommentsClient()

    comments = await client.get_show_comments(show_id, limit=limit, sort=sort)

    # Handle transitional case where API returns error strings
    if isinstance(comments, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="show_comments",
            resource_id=show_id,
            error_message=comments,
            operation="fetch_show_comments",
        )

    title = f"Show ID: {show_id}"
    return CommentsFormatters.format_comments(
        comments,
        title,
        show_spoilers=show_spoilers,
    )


@handle_api_errors_func
async def fetch_season_comments(
    show_id: str,
    season: int,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: CommentSort = "newest",
) -> str:
    """Fetch comments for a season from Trakt.

    Args:
        show_id: Trakt ID of the show
        season: Season number
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies)

    Returns:
        Information about season comments

    Raises:
        InvalidParamsError: If show_id or season is invalid
        InternalError: If an error occurs fetching comments
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = SeasonParam(show_id=show_id, season=season)
    show_id, season = params.show_id, params.season

    client = SeasonCommentsClient()

    comments = await client.get_season_comments(show_id, season, limit=limit, sort=sort)

    # Handle transitional case where API returns error strings
    if isinstance(comments, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_comments",
            resource_id=f"{show_id}-{season}",
            error_message=comments,
            operation="fetch_season_comments",
        )

    title = f"Show ID: {show_id} - Season {season}"
    return CommentsFormatters.format_comments(
        comments,
        title,
        show_spoilers=show_spoilers,
    )


@handle_api_errors_func
async def fetch_episode_comments(
    show_id: str,
    season: int,
    episode: int,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: CommentSort = "newest",
) -> str:
    """Fetch comments for an episode from Trakt.

    Args:
        show_id: Trakt ID of the show
        season: Season number
        episode: Episode number
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies)

    Returns:
        Information about episode comments

    Raises:
        InvalidParamsError: If show_id, season, or episode is invalid
        InternalError: If an error occurs fetching comments
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = EpisodeParam(show_id=show_id, season=season, episode=episode)
    show_id, season, episode = params.show_id, params.season, params.episode

    client = EpisodeCommentsClient()

    comments = await client.get_episode_comments(
        show_id, season, episode, limit=limit, sort=sort
    )

    # Handle transitional case where API returns error strings
    if isinstance(comments, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode_comments",
            resource_id=f"{show_id}-{season}-{episode}",
            error_message=comments,
            operation="fetch_episode_comments",
        )

    title = f"Show ID: {show_id} - S{season:02d}E{episode:02d}"
    return CommentsFormatters.format_comments(
        comments,
        title,
        show_spoilers=show_spoilers,
    )


@handle_api_errors_func
async def fetch_comment(comment_id: str, show_spoilers: bool = False) -> str:
    """Fetch a specific comment from Trakt.

    Args:
        comment_id: Trakt ID of the comment
        show_spoilers: Whether to show spoilers by default

    Returns:
        Information about the comment

    Raises:
        InvalidParamsError: If comment_id is invalid
        InternalError: If an error occurs fetching comment
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = CommentIdParam(comment_id=comment_id)
    comment_id = params.comment_id

    client = CommentDetailsClient()

    comment = await client.get_comment(comment_id)

    # Handle transitional case where API returns error strings
    if isinstance(comment, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="comment",
            resource_id=comment_id,
            error_message=comment,
            operation="fetch_comment",
        )

    return CommentsFormatters.format_comment(comment, show_spoilers=show_spoilers)


@handle_api_errors_func
async def fetch_comment_replies(
    comment_id: str,
    limit: int = DEFAULT_LIMIT,
    show_spoilers: bool = False,
    sort: CommentSort = "newest",
) -> str:
    """Fetch replies for a comment from Trakt.

    Args:
        comment_id: Trakt ID of the comment
        limit: Maximum number of replies to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort replies (newest, oldest, likes, replies)

    Returns:
        Information about the comment and its replies

    Raises:
        InvalidParamsError: If comment_id is invalid
        InternalError: If an error occurs fetching comment replies
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = CommentIdParam(comment_id=comment_id)
    comment_id = params.comment_id

    client = CommentDetailsClient()

    comment = await client.get_comment(comment_id)

    # Handle transitional case where API returns error strings
    if isinstance(comment, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="comment",
            resource_id=comment_id,
            error_message=comment,
            operation="fetch_comment_replies",
        )

    replies = await client.get_comment_replies(comment_id, limit=limit, sort=sort)

    # Handle transitional case where API returns error strings
    if isinstance(replies, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="comment_replies",
            resource_id=comment_id,
            error_message=replies,
            operation="fetch_comment_replies",
        )

    return CommentsFormatters.format_comment(
        comment,
        with_replies=True,
        replies=replies,
        show_spoilers=show_spoilers,
    )


def register_comment_tools(
    mcp: FastMCP,
) -> tuple[
    MovieCommentsToolType,
    ShowCommentsToolType,
    SeasonCommentsToolType,
    EpisodeCommentsToolType,
    CommentToolType,
    CommentRepliesToolType,
]:
    """Register comment tools with the MCP server.

    Args:
        mcp: FastMCP instance used to register tool handlers.

    Returns:
        Tuple of tool handlers for type-checker visibility.
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_movie_comments"],
        description="Fetch comments for a specific movie from Trakt",
    )
    async def fetch_movie_comments_tool(
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        show_spoilers: bool = False,
        sort: CommentSort = "newest",
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
        sort: CommentSort = "newest",
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
        sort: CommentSort = "newest",
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
        sort: CommentSort = "newest",
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
        sort: CommentSort = "newest",
    ) -> str:
        return await fetch_comment_replies(comment_id, limit, show_spoilers, sort)

    # Return handlers for type checker visibility
    return (
        fetch_movie_comments_tool,
        fetch_show_comments_tool,
        fetch_season_comments_tool,
        fetch_episode_comments_tool,
        fetch_comment_tool,
        fetch_comment_replies_tool,
    )
