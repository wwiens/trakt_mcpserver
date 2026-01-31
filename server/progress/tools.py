"""Progress tools for the Trakt MCP server."""

import logging
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from client.progress.client import ProgressClient
from config.mcp.descriptions import (
    PLAYBACK_ID_DESCRIPTION,
    PLAYBACK_TYPE_DESCRIPTION,
    SHOW_ID_DESCRIPTION,
    SHOW_PROGRESS_COUNT_SPECIALS_DESCRIPTION,
    SHOW_PROGRESS_HIDDEN_DESCRIPTION,
    SHOW_PROGRESS_LAST_ACTIVITY_DESCRIPTION,
    SHOW_PROGRESS_SPECIALS_DESCRIPTION,
    SHOW_PROGRESS_VERBOSE_DESCRIPTION,
)
from config.mcp.tools.progress import PROGRESS_TOOLS
from models.formatters.progress import ProgressFormatters
from server.base import BaseToolErrorMixin
from utils.api.errors import handle_api_errors_func

logger = logging.getLogger("trakt_mcp")

# Type alias for tool handlers
ToolHandler = Callable[..., Awaitable[str]]


@handle_api_errors_func
async def fetch_show_progress(
    show_id: str,
    hidden: bool = False,
    specials: bool = False,
    count_specials: bool = True,
    last_activity: Literal["aired", "watched"] = "aired",
    verbose: bool = False,
) -> str:
    """Fetch watched progress for a TV show.

    Args:
        show_id: Trakt ID, slug, or IMDB ID of the show
        hidden: Include hidden seasons in progress calculation
        specials: Include specials as season 0 in progress
        count_specials: Count specials in overall stats when specials included
        last_activity: Calculate last/next episode based on 'aired' or 'watched'
        verbose: Show episode-by-episode watch dates

    Returns:
        Show progress formatted as markdown

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("fetch_show_progress called with show_id=%s", show_id)

    client = ProgressClient()

    result = await client.get_show_progress(
        show_id,
        hidden=hidden,
        specials=specials,
        count_specials=count_specials,
        last_activity=last_activity,
    )

    # Handle transitional case where API returns error strings
    if isinstance(result, str):
        error = BaseToolErrorMixin.handle_api_string_error(
            resource_type="show_progress",
            resource_id=show_id,
            error_message=result,
            operation="fetch_show_progress",
        )
        raise error

    return ProgressFormatters.format_show_progress(result, show_id, verbose=verbose)


@handle_api_errors_func
async def fetch_playback_progress(
    playback_type: Literal["movies", "episodes"] | None = None,
) -> str:
    """Fetch paused playback progress items.

    Args:
        playback_type: Filter by type ('movies', 'episodes'), or None for all

    Returns:
        Playback progress items formatted as markdown

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("fetch_playback_progress called with type=%s", playback_type)

    client = ProgressClient()

    result = await client.get_playback_progress(playback_type)

    # Handle transitional case where API returns error strings
    if isinstance(result, str):
        error = BaseToolErrorMixin.handle_api_string_error(
            resource_type="playback_progress",
            resource_id=playback_type or "all",
            error_message=result,
            operation="fetch_playback_progress",
        )
        raise error

    return ProgressFormatters.format_playback_progress(result)


@handle_api_errors_func
async def remove_playback_item(playback_id: int) -> str:
    """Remove a playback progress item.

    Args:
        playback_id: ID of the playback item to remove

    Returns:
        Confirmation message

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("remove_playback_item called with id=%s", playback_id)

    client = ProgressClient()

    await client.remove_playback_item(playback_id)

    return f"Successfully removed playback item with ID {playback_id}."


def register_progress_tools(
    mcp: FastMCP,
) -> tuple[ToolHandler, ToolHandler, ToolHandler]:
    """Register progress tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=PROGRESS_TOOLS["fetch_show_progress"],
        description=(
            "Check if a user has watched a specific TV show and their progress through it. "
            "Use this for: 'have I seen X?', 'did I finish X?', 'where am I in X?', 'what episode am I on?'. "
            "Returns episodes watched, completion percentage, next episode to watch, and per-season breakdown. "
            "For listing all watched shows, use fetch_user_watched_shows instead. "
            "Requires OAuth authentication."
        ),
    )
    async def fetch_show_progress_tool(
        show_id: Annotated[str, Field(description=SHOW_ID_DESCRIPTION)],
        hidden: Annotated[
            bool, Field(description=SHOW_PROGRESS_HIDDEN_DESCRIPTION)
        ] = False,
        specials: Annotated[
            bool, Field(description=SHOW_PROGRESS_SPECIALS_DESCRIPTION)
        ] = False,
        count_specials: Annotated[
            bool, Field(description=SHOW_PROGRESS_COUNT_SPECIALS_DESCRIPTION)
        ] = True,
        last_activity: Annotated[
            Literal["aired", "watched"],
            Field(description=SHOW_PROGRESS_LAST_ACTIVITY_DESCRIPTION),
        ] = "aired",
        verbose: Annotated[
            bool, Field(description=SHOW_PROGRESS_VERBOSE_DESCRIPTION)
        ] = False,
    ) -> str:
        return await fetch_show_progress(
            show_id, hidden, specials, count_specials, last_activity, verbose
        )

    @mcp.tool(
        name=PROGRESS_TOOLS["fetch_playback_progress"],
        description=(
            "Fetch paused playback progress items. Shows movies and episodes "
            "that were paused during playback with their progress percentage. "
            "Requires OAuth authentication."
        ),
    )
    async def fetch_playback_progress_tool(
        playback_type: Annotated[
            Literal["movies", "episodes"] | None,
            Field(description=PLAYBACK_TYPE_DESCRIPTION),
        ] = None,
    ) -> str:
        return await fetch_playback_progress(playback_type)

    @mcp.tool(
        name=PROGRESS_TOOLS["remove_playback_item"],
        description=(
            "Remove a paused playback progress item. Use the ID from "
            "fetch_playback_progress results. Requires OAuth authentication."
        ),
    )
    async def remove_playback_item_tool(
        playback_id: Annotated[int, Field(description=PLAYBACK_ID_DESCRIPTION)],
    ) -> str:
        return await remove_playback_item(playback_id)

    # Return handlers for type checker visibility
    return (
        fetch_show_progress_tool,
        fetch_playback_progress_tool,
        remove_playback_item_tool,
    )
