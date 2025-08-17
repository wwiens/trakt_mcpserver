"""Comment tools for the Trakt MCP server."""

from collections.abc import Awaitable, Callable
from typing import Literal, NoReturn, TypedDict

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, PositiveInt, ValidationError, field_validator

from client.comments.details import CommentDetailsClient
from client.comments.episode import EpisodeCommentsClient
from client.comments.movie import MovieCommentsClient
from client.comments.season import SeasonCommentsClient
from client.comments.show import ShowCommentsClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools import TOOL_NAMES
from models.formatters.comments import CommentsFormatters
from models.types import CommentResponse
from server.base import BaseToolErrorMixin
from server.movies.tools import MovieIdParam
from server.shows.tools import ShowIdParam
from utils.api.errors import handle_api_errors_func

# Comment sort options supported by Trakt API
CommentSort = Literal["newest", "oldest", "likes", "replies"]


class ValidationErrorDetail(TypedDict):
    """Typed structure for validation error details."""

    field: str
    message: str
    type: str
    input: object | None


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


class CommentsListOptionsParam(BaseModel):
    """Parameters for comment listing tools with validation constraints."""

    limit: PositiveInt = Field(
        DEFAULT_LIMIT,
        le=200,
        description="Maximum number of comments to return (1-200)",
    )
    sort: CommentSort = Field("newest", description="Sort order for comments")
    show_spoilers: bool = Field(False, description="Whether to show spoiler content")


def _handle_validation_error(e: ValidationError, context: str) -> NoReturn:
    """Handle validation errors with consistent formatting via BaseToolErrorMixin.

    Args:
        e: The ValidationError to handle
        context: Context string for the error message

    Raises:
        BaseToolErrorMixin error: Formatted validation error via mixin
    """
    validation_errors: list[ValidationErrorDetail] = [
        ValidationErrorDetail(
            field=str(error.get("loc", [context])[-1]),
            message=str(error.get("msg", "Invalid value")),
            type=str(error.get("type", "validation_error")),
            input=error.get("input"),
        )
        for error in e.errors()
    ]

    raise BaseToolErrorMixin.handle_validation_error(
        f"Invalid parameters for {context}",
        validation_errors=validation_errors,
        operation=f"{context.replace(' ', '_')}_validation",
    ) from e


def _ensure_not_error_string(
    value: object, *, resource_type: str, resource_id: str, operation: str
) -> None:
    """Helper to check if API response is an error string and raise appropriate error.

    Args:
        value: The API response value to check
        resource_type: Type of resource for error context
        resource_id: ID of the resource for error context
        operation: Operation being performed for error context

    Raises:
        BaseToolErrorMixin error: If value is an error string
    """
    if isinstance(value, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type=resource_type,
            resource_id=resource_id,
            error_message=value,
            operation=operation,
        )


async def _fetch_and_format_comments(
    *,
    resource_type: str,
    resource_id: str,
    fetch_fn: Callable[[], Awaitable[list[CommentResponse]]],
    title: str,
    show_spoilers: bool,
) -> str:
    """Helper to reduce duplication in comment fetching functions.

    Args:
        resource_type: Type of resource for error context (e.g., "movie_comments")
        resource_id: ID of the resource for error context
        fetch_fn: Zero-argument callable that performs the client API call
        title: Title to use in formatted output
        show_spoilers: Whether to show spoiler content

    Returns:
        Formatted comments as markdown string

    Raises:
        BaseToolErrorMixin error: If API response is an error string
    """
    data = await fetch_fn()
    _ensure_not_error_string(
        data,
        resource_type=resource_type,
        resource_id=resource_id,
        operation=f"fetch_{resource_type}",
    )
    return CommentsFormatters.format_comments(data, title, show_spoilers=show_spoilers)


async def _fetch_and_format_comment(
    *,
    resource_type: str,
    resource_id: str,
    fetch_fn: Callable[[], Awaitable[CommentResponse]],
    show_spoilers: bool,
) -> str:
    """Helper to reduce duplication in single comment fetching functions.

    Args:
        resource_type: Type of resource for error context (e.g., "comment")
        resource_id: ID of the resource for error context
        fetch_fn: Zero-argument callable that performs the client API call
        show_spoilers: Whether to show spoiler content

    Returns:
        Formatted comment as markdown string

    Raises:
        BaseToolErrorMixin error: If API response is an error string
    """
    data = await fetch_fn()
    _ensure_not_error_string(
        data,
        resource_type=resource_type,
        resource_id=resource_id,
        operation=f"fetch_{resource_type}",
    )
    return CommentsFormatters.format_comment(data, show_spoilers=show_spoilers)


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
    try:
        id_params = MovieIdParam(movie_id=movie_id)
        options = CommentsListOptionsParam(
            limit=limit, sort=sort, show_spoilers=show_spoilers
        )
        movie_id = id_params.movie_id
    except ValidationError as e:
        _handle_validation_error(e, "movie comments")

    client = MovieCommentsClient()

    return await _fetch_and_format_comments(
        resource_type="movie_comments",
        resource_id=movie_id,
        fetch_fn=lambda: client.get_movie_comments(
            movie_id, limit=options.limit, sort=options.sort
        ),
        title=f"Movie ID: {movie_id}",
        show_spoilers=options.show_spoilers,
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
    try:
        id_params = ShowIdParam(show_id=show_id)
        options = CommentsListOptionsParam(
            limit=limit, sort=sort, show_spoilers=show_spoilers
        )
        show_id = id_params.show_id
    except ValidationError as e:
        _handle_validation_error(e, "show comments")

    client = ShowCommentsClient()

    return await _fetch_and_format_comments(
        resource_type="show_comments",
        resource_id=show_id,
        fetch_fn=lambda: client.get_show_comments(
            show_id, limit=options.limit, sort=options.sort
        ),
        title=f"Show ID: {show_id}",
        show_spoilers=options.show_spoilers,
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
    try:
        id_params = SeasonParam(show_id=show_id, season=season)
        options = CommentsListOptionsParam(
            limit=limit, sort=sort, show_spoilers=show_spoilers
        )
        show_id, season = id_params.show_id, id_params.season
    except ValidationError as e:
        _handle_validation_error(e, "season comments")

    client = SeasonCommentsClient()

    return await _fetch_and_format_comments(
        resource_type="season_comments",
        resource_id=f"{show_id}-{season}",
        fetch_fn=lambda: client.get_season_comments(
            show_id, season, limit=options.limit, sort=options.sort
        ),
        title=f"Show ID: {show_id} - Season {season}",
        show_spoilers=options.show_spoilers,
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
    try:
        id_params = EpisodeParam(show_id=show_id, season=season, episode=episode)
        options = CommentsListOptionsParam(
            limit=limit, sort=sort, show_spoilers=show_spoilers
        )
        show_id, season, episode = (
            id_params.show_id,
            id_params.season,
            id_params.episode,
        )
    except ValidationError as e:
        _handle_validation_error(e, "episode comments")

    client = EpisodeCommentsClient()

    return await _fetch_and_format_comments(
        resource_type="episode_comments",
        resource_id=f"{show_id}-{season}-{episode}",
        fetch_fn=lambda: client.get_episode_comments(
            show_id, season, episode, limit=options.limit, sort=options.sort
        ),
        title=f"Show ID: {show_id} - S{season:02d}E{episode:02d}",
        show_spoilers=options.show_spoilers,
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
    try:
        params = CommentIdParam(comment_id=comment_id)
        comment_id = params.comment_id
    except ValidationError as e:
        _handle_validation_error(e, "comment")

    client = CommentDetailsClient()

    return await _fetch_and_format_comment(
        resource_type="comment",
        resource_id=comment_id,
        fetch_fn=lambda: client.get_comment(comment_id),
        show_spoilers=show_spoilers,
    )


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
    try:
        id_params = CommentIdParam(comment_id=comment_id)
        options = CommentsListOptionsParam(
            limit=limit, sort=sort, show_spoilers=show_spoilers
        )
        comment_id = id_params.comment_id
    except ValidationError as e:
        _handle_validation_error(e, "comment replies")

    client = CommentDetailsClient()

    # Fetch comment data
    comment = await client.get_comment(comment_id)
    _ensure_not_error_string(
        comment,
        resource_type="comment",
        resource_id=comment_id,
        operation="fetch_comment_replies",
    )

    # Fetch replies data
    replies = await client.get_comment_replies(
        comment_id, limit=options.limit, sort=options.sort
    )
    _ensure_not_error_string(
        replies,
        resource_type="comment_replies",
        resource_id=comment_id,
        operation="fetch_comment_replies",
    )

    return CommentsFormatters.format_comment(
        comment,
        with_replies=True,
        replies=replies,
        show_spoilers=options.show_spoilers,
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
