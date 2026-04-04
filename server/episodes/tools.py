"""Episode tools for the Trakt MCP server."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Annotated, Final, Literal, TypeAlias

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from client.episodes.lists import EpisodeListsClient
from client.episodes.people import EpisodePeopleClient
from client.episodes.ratings import EpisodeRatingsClient
from client.episodes.stats import EpisodeStatsClient
from client.episodes.summary import EpisodeSummaryClient
from client.episodes.translations import EpisodeTranslationsClient
from client.episodes.videos import EpisodeVideosClient
from client.episodes.watching import EpisodeWatchingClient
from client.shows.details import ShowDetailsClient
from config.api.lists import (
    INVALID_LIST_SORT_MSG,
    INVALID_LIST_TYPE_MSG,
    VALID_LIST_SORTS,
    VALID_LIST_TYPES,
)
from config.mcp.descriptions import (
    EMBED_MARKDOWN_DESCRIPTION,
    EPISODE_DESCRIPTION,
    LANGUAGE_DESCRIPTION,
    LIST_SORT_DESCRIPTION,
    LIST_TYPE_DESCRIPTION,
    SEASON_DESCRIPTION,
    SHOW_ID_DESCRIPTION,
)
from config.mcp.tools import TOOL_NAMES
from models.formatters.episodes import EpisodeFormatters
from models.formatters.videos import VideoFormatters
from models.types.language import validate_language
from server.base import BaseToolErrorMixin
from utils.api.errors import handle_api_errors_func

if TYPE_CHECKING:
    from models.types import ShowResponse

logger = logging.getLogger("trakt_mcp")

ToolHandler: TypeAlias = Callable[..., Awaitable[str]]

INVALID_LANGUAGE_MSG: Final[str] = "Language must be 'all' or a 2-letter ISO 639-1 code"


class EpisodeIdParam(BaseModel):
    """Parameters for tools that require a show ID, season, and episode number."""

    show_id: str = Field(
        ...,
        min_length=1,
        description=SHOW_ID_DESCRIPTION,
    )
    season: int = Field(
        ...,
        ge=0,
        description=SEASON_DESCRIPTION,
    )
    episode: int = Field(
        ...,
        ge=1,
        description=EPISODE_DESCRIPTION,
    )

    @field_validator("show_id", mode="before")
    @classmethod
    def _strip_show_id(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


async def _get_show_title(show_id: str) -> str:
    """Fetch the show title for use in formatted responses.

    Falls back to ``Show ID: <show_id>`` when the lookup fails for any reason
    so callers always receive a usable title string.

    Args:
        show_id: Trakt ID, slug, or IMDB ID

    Returns:
        Show title string, or fallback ``Show ID: <show_id>`` on failure
    """
    try:
        show_client = ShowDetailsClient()
        show_data: ShowResponse | str = await show_client.get_show(show_id)

        if isinstance(show_data, str):
            return f"Show ID: {show_id}"

        return show_data.get("title", f"Show ID: {show_id}")
    except Exception as exc:
        logger.debug(
            "Non-fatal exception during show title lookup; falling back to ID title.",
            exc_info=True,
            extra={
                "resource_id": show_id,
                "operation": "fetch_show_title",
                "error": str(exc),
            },
        )
        return f"Show ID: {show_id}"


@handle_api_errors_func
async def fetch_episode_summary(show_id: str, season: int, episode: int) -> str:
    """Fetch details for a specific episode.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        episode: Episode number

    Returns:
        Formatted markdown with episode details
    """
    params = EpisodeIdParam(show_id=show_id, season=season, episode=episode)

    client = EpisodeSummaryClient()
    show_title, episode_data = await asyncio.gather(
        _get_show_title(params.show_id),
        client.get_episode(params.show_id, params.season, params.episode),
    )

    if isinstance(episode_data, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode",
            resource_id=f"{params.show_id}/S{params.season:02d}E{params.episode:02d}",
            error_message=episode_data,
            operation="fetch_episode_summary",
        )

    return EpisodeFormatters.format_episode_summary(episode_data, show_title)


@handle_api_errors_func
async def fetch_episode_ratings(show_id: str, season: int, episode: int) -> str:
    """Fetch ratings for a specific episode.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        episode: Episode number

    Returns:
        Formatted markdown with ratings and distribution
    """
    params = EpisodeIdParam(show_id=show_id, season=season, episode=episode)

    ratings_client = EpisodeRatingsClient()
    show_title, ratings = await asyncio.gather(
        _get_show_title(params.show_id),
        ratings_client.get_episode_ratings(
            params.show_id, params.season, params.episode
        ),
    )

    if isinstance(ratings, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode_ratings",
            resource_id=f"{params.show_id}/S{params.season:02d}E{params.episode:02d}",
            error_message=ratings,
            operation="fetch_episode_ratings",
            show_title=show_title,
        )

    return EpisodeFormatters.format_episode_ratings(
        ratings, show_title, params.season, params.episode
    )


@handle_api_errors_func
async def fetch_episode_stats(show_id: str, season: int, episode: int) -> str:
    """Fetch statistics for a specific episode.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        episode: Episode number

    Returns:
        Formatted markdown with episode statistics
    """
    params = EpisodeIdParam(show_id=show_id, season=season, episode=episode)

    stats_client = EpisodeStatsClient()
    show_title, stats = await asyncio.gather(
        _get_show_title(params.show_id),
        stats_client.get_episode_stats(params.show_id, params.season, params.episode),
    )

    if isinstance(stats, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode_stats",
            resource_id=f"{params.show_id}/S{params.season:02d}E{params.episode:02d}",
            error_message=stats,
            operation="fetch_episode_stats",
            show_title=show_title,
        )

    return EpisodeFormatters.format_episode_stats(
        stats, show_title, params.season, params.episode
    )


@handle_api_errors_func
async def fetch_episode_people(show_id: str, season: int, episode: int) -> str:
    """Fetch cast and crew for a specific episode.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        episode: Episode number

    Returns:
        Formatted markdown with cast and crew
    """
    params = EpisodeIdParam(show_id=show_id, season=season, episode=episode)

    people_client = EpisodePeopleClient()
    show_title, people = await asyncio.gather(
        _get_show_title(params.show_id),
        people_client.get_episode_people(params.show_id, params.season, params.episode),
    )

    if isinstance(people, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode_people",
            resource_id=f"{params.show_id}/S{params.season:02d}E{params.episode:02d}",
            error_message=people,
            operation="fetch_episode_people",
            show_title=show_title,
        )

    return EpisodeFormatters.format_episode_people(
        people, show_title, params.season, params.episode
    )


@handle_api_errors_func
async def fetch_episode_videos(
    show_id: str, season: int, episode: int, embed_markdown: bool = True
) -> str:
    """Fetch videos for a specific episode.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        episode: Episode number
        embed_markdown: Use embedded markdown syntax for video links

    Returns:
        Formatted markdown with videos
    """
    params = EpisodeIdParam(show_id=show_id, season=season, episode=episode)

    videos_client = EpisodeVideosClient()
    title, videos = await asyncio.gather(
        _get_show_title(params.show_id),
        videos_client.get_episode_videos(params.show_id, params.season, params.episode),
    )

    if isinstance(videos, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode_videos",
            resource_id=f"{params.show_id}/S{params.season:02d}E{params.episode:02d}",
            error_message=videos,
            operation="fetch_episode_videos",
        )

    episode_title = f"{title} - S{params.season:02d}E{params.episode:02d}"
    return VideoFormatters.format_videos_list(
        videos, episode_title, embed_markdown, validate_input=False
    )


@handle_api_errors_func
async def fetch_episode_watching(show_id: str, season: int, episode: int) -> str:
    """Fetch users currently watching a specific episode.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        episode: Episode number

    Returns:
        Formatted markdown with user list
    """
    params = EpisodeIdParam(show_id=show_id, season=season, episode=episode)

    watching_client = EpisodeWatchingClient()
    show_title, users = await asyncio.gather(
        _get_show_title(params.show_id),
        watching_client.get_episode_watching(
            params.show_id, params.season, params.episode
        ),
    )

    if isinstance(users, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode_watching",
            resource_id=f"{params.show_id}/S{params.season:02d}E{params.episode:02d}",
            error_message=users,
            operation="fetch_episode_watching",
            show_title=show_title,
        )

    return EpisodeFormatters.format_episode_watching(
        users, show_title, params.season, params.episode
    )


@handle_api_errors_func
async def fetch_episode_translations(
    show_id: str, season: int, episode: int, language: str = "all"
) -> str:
    """Fetch translations for a specific episode.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        episode: Episode number
        language: 2-character language code or 'all'

    Returns:
        Formatted markdown with translations
    """
    params = EpisodeIdParam(show_id=show_id, season=season, episode=episode)

    try:
        language = validate_language(language)
    except ValueError as err:
        raise BaseToolErrorMixin.handle_validation_error(
            INVALID_LANGUAGE_MSG,
            parameter="language",
            provided_value=language,
        ) from err

    translations_client = EpisodeTranslationsClient()
    show_title, translations = await asyncio.gather(
        _get_show_title(params.show_id),
        translations_client.get_episode_translations(
            params.show_id, params.season, params.episode, language
        ),
    )

    if isinstance(translations, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode_translations",
            resource_id=f"{params.show_id}/S{params.season:02d}E{params.episode:02d}",
            error_message=translations,
            operation="fetch_episode_translations",
            show_title=show_title,
        )

    return EpisodeFormatters.format_episode_translations(
        translations, show_title, params.season, params.episode
    )


@handle_api_errors_func
async def fetch_episode_lists(
    show_id: str,
    season: int,
    episode: int,
    list_type: str = "all",
    sort: str = "popular",
) -> str:
    """Fetch lists containing a specific episode.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        episode: Episode number
        list_type: Filter by type: 'all', 'personal', 'official', 'watchlists'
        sort: Sort order: 'popular', 'likes', 'comments', 'items', 'added', 'updated'

    Returns:
        Formatted markdown with lists
    """
    params = EpisodeIdParam(show_id=show_id, season=season, episode=episode)

    if list_type not in VALID_LIST_TYPES:
        raise BaseToolErrorMixin.handle_validation_error(
            INVALID_LIST_TYPE_MSG,
            parameter="list_type",
            provided_value=list_type,
        )
    if sort not in VALID_LIST_SORTS:
        raise BaseToolErrorMixin.handle_validation_error(
            INVALID_LIST_SORT_MSG,
            parameter="sort",
            provided_value=sort,
        )

    lists_client = EpisodeListsClient()
    show_title, lists = await asyncio.gather(
        _get_show_title(params.show_id),
        lists_client.get_episode_lists(
            params.show_id, params.season, params.episode, list_type, sort
        ),
    )

    if isinstance(lists, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="episode_lists",
            resource_id=f"{params.show_id}/S{params.season:02d}E{params.episode:02d}",
            error_message=lists,
            operation="fetch_episode_lists",
            show_title=show_title,
        )

    return EpisodeFormatters.format_episode_lists(
        lists, show_title, params.season, params.episode
    )


def register_episode_tools(mcp: FastMCP) -> tuple[ToolHandler, ...]:
    """Register episode tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_summary"],
        description=(
            "Fetch detailed information about a specific TV show episode, "
            "including overview, air date, runtime, and ratings."
        ),
    )
    async def fetch_episode_summary_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(ge=1, description=EPISODE_DESCRIPTION)],
    ) -> str:
        return await fetch_episode_summary(show_id, season, episode)

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_ratings"],
        description=(
            "Fetch ratings and voting statistics for a specific TV show episode."
        ),
    )
    async def fetch_episode_ratings_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(ge=1, description=EPISODE_DESCRIPTION)],
    ) -> str:
        return await fetch_episode_ratings(show_id, season, episode)

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_stats"],
        description=(
            "Fetch engagement statistics for a specific TV show episode "
            "including watchers, plays, collectors, and comments."
        ),
    )
    async def fetch_episode_stats_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(ge=1, description=EPISODE_DESCRIPTION)],
    ) -> str:
        return await fetch_episode_stats(show_id, season, episode)

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_people"],
        description=(
            "Fetch cast and crew for a specific TV show episode, "
            "including character names and episode counts."
        ),
    )
    async def fetch_episode_people_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(ge=1, description=EPISODE_DESCRIPTION)],
    ) -> str:
        return await fetch_episode_people(show_id, season, episode)

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_videos"],
        description=(
            "Fetch videos (trailers, recaps, etc.) for a specific TV show episode. "
            "Set embed_markdown=False for simple links."
        ),
    )
    async def fetch_episode_videos_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(ge=1, description=EPISODE_DESCRIPTION)],
        embed_markdown: Annotated[
            bool,
            Field(description=EMBED_MARKDOWN_DESCRIPTION),
        ] = True,
    ) -> str:
        return await fetch_episode_videos(show_id, season, episode, embed_markdown)

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_watching"],
        description=(
            "Fetch users currently watching a specific TV show episode right now."
        ),
    )
    async def fetch_episode_watching_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(ge=1, description=EPISODE_DESCRIPTION)],
    ) -> str:
        return await fetch_episode_watching(show_id, season, episode)

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_translations"],
        description=(
            "Fetch translations for a specific TV show episode in different languages."
        ),
    )
    async def fetch_episode_translations_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(ge=1, description=EPISODE_DESCRIPTION)],
        language: Annotated[str, Field(description=LANGUAGE_DESCRIPTION)] = "all",
    ) -> str:
        return await fetch_episode_translations(show_id, season, episode, language)

    @mcp.tool(
        name=TOOL_NAMES["fetch_episode_lists"],
        description="Fetch lists that contain a specific TV show episode.",
    )
    async def fetch_episode_lists_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        episode: Annotated[int, Field(ge=1, description=EPISODE_DESCRIPTION)],
        list_type: Annotated[
            Literal["all", "personal", "official", "watchlists"],
            Field(description=LIST_TYPE_DESCRIPTION),
        ] = "all",
        sort: Annotated[
            Literal["popular", "likes", "comments", "items", "added", "updated"],
            Field(description=LIST_SORT_DESCRIPTION),
        ] = "popular",
    ) -> str:
        return await fetch_episode_lists(show_id, season, episode, list_type, sort)

    return (
        fetch_episode_summary_tool,
        fetch_episode_ratings_tool,
        fetch_episode_stats_tool,
        fetch_episode_people_tool,
        fetch_episode_videos_tool,
        fetch_episode_watching_tool,
        fetch_episode_translations_tool,
        fetch_episode_lists_tool,
    )
