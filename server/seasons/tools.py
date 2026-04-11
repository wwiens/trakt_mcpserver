"""Season tools for the Trakt MCP server."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Annotated, Final, Literal, TypeAlias

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from client.seasons.episodes import SeasonEpisodesClient
from client.seasons.info import SeasonInfoClient
from client.seasons.lists import SeasonListsClient
from client.seasons.people import SeasonPeopleClient
from client.seasons.ratings import SeasonRatingsClient
from client.seasons.stats import SeasonStatsClient
from client.seasons.translations import SeasonTranslationsClient
from client.seasons.videos import SeasonVideosClient
from client.seasons.watching import SeasonWatchingClient
from client.shows.details import ShowDetailsClient
from config.api.lists import (
    INVALID_LIST_SORT_MSG,
    INVALID_LIST_TYPE_MSG,
    VALID_LIST_SORTS,
    VALID_LIST_TYPES,
)
from config.mcp.descriptions import (
    EMBED_MARKDOWN_DESCRIPTION,
    LANGUAGE_DESCRIPTION,
    LIST_SORT_DESCRIPTION,
    LIST_TYPE_DESCRIPTION,
    SEASON_DESCRIPTION,
    SHOW_ID_DESCRIPTION,
)
from config.mcp.tools import TOOL_NAMES
from models.formatters.seasons import SeasonFormatters
from models.formatters.videos import VideoFormatters
from models.types.language import validate_language
from server.base import BaseToolErrorMixin
from utils.api.errors import handle_api_errors_func

if TYPE_CHECKING:
    from models.types import (
        EpisodeResponse,
        SeasonResponse,
        ShowResponse,
    )

logger = logging.getLogger("trakt_mcp")

ToolHandler: TypeAlias = Callable[..., Awaitable[str]]

INVALID_LANGUAGE_MSG: Final[str] = "Language must be 'all' or a 2-letter ISO 639-1 code"


class SeasonIdParam(BaseModel):
    """Parameters for tools that require a show ID and season number."""

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
async def fetch_season_info(show_id: str, season: int) -> str:
    """Fetch details for a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)

    Returns:
        Formatted markdown with season details
    """
    params = SeasonIdParam(show_id=show_id, season=season)

    client = SeasonInfoClient()
    season_data: SeasonResponse | str = await client.get_season(
        params.show_id, params.season
    )

    if isinstance(season_data, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=season_data,
            operation="fetch_season_info",
        )

    return SeasonFormatters.format_season_info(season_data)


@handle_api_errors_func
async def fetch_season_episodes(show_id: str, season: int) -> str:
    """Fetch all episodes for a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)

    Returns:
        Formatted markdown with episode list
    """
    params = SeasonIdParam(show_id=show_id, season=season)

    client = SeasonEpisodesClient()
    episodes: list[EpisodeResponse] | str = await client.get_season_episodes(
        params.show_id, params.season
    )

    if isinstance(episodes, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_episodes",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=episodes,
            operation="fetch_season_episodes",
        )

    return SeasonFormatters.format_season_episodes(episodes, params.season)


@handle_api_errors_func
async def fetch_season_ratings(show_id: str, season: int) -> str:
    """Fetch ratings for a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)

    Returns:
        Formatted markdown with ratings and distribution
    """
    params = SeasonIdParam(show_id=show_id, season=season)

    ratings_client = SeasonRatingsClient()
    show_title, ratings = await asyncio.gather(
        _get_show_title(params.show_id),
        ratings_client.get_season_ratings(params.show_id, params.season),
    )

    if isinstance(ratings, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_ratings",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=ratings,
            operation="fetch_season_ratings",
            show_title=show_title,
        )

    return SeasonFormatters.format_season_ratings(ratings, show_title, params.season)


@handle_api_errors_func
async def fetch_season_stats(show_id: str, season: int) -> str:
    """Fetch statistics for a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)

    Returns:
        Formatted markdown with season statistics
    """
    params = SeasonIdParam(show_id=show_id, season=season)

    stats_client = SeasonStatsClient()
    show_title, stats = await asyncio.gather(
        _get_show_title(params.show_id),
        stats_client.get_season_stats(params.show_id, params.season),
    )

    if isinstance(stats, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_stats",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=stats,
            operation="fetch_season_stats",
            show_title=show_title,
        )

    return SeasonFormatters.format_season_stats(stats, show_title, params.season)


@handle_api_errors_func
async def fetch_season_people(show_id: str, season: int) -> str:
    """Fetch cast and crew for a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)

    Returns:
        Formatted markdown with cast and crew
    """
    params = SeasonIdParam(show_id=show_id, season=season)

    people_client = SeasonPeopleClient()
    show_title, people = await asyncio.gather(
        _get_show_title(params.show_id),
        people_client.get_season_people(params.show_id, params.season),
    )

    if isinstance(people, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_people",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=people,
            operation="fetch_season_people",
            show_title=show_title,
        )

    return SeasonFormatters.format_season_people(people, show_title, params.season)


@handle_api_errors_func
async def fetch_season_videos(
    show_id: str, season: int, embed_markdown: bool = True
) -> str:
    """Fetch videos for a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        embed_markdown: Use embedded markdown syntax for video links

    Returns:
        Formatted markdown with videos
    """
    params = SeasonIdParam(show_id=show_id, season=season)

    videos_client = SeasonVideosClient()
    videos, title = await asyncio.gather(
        videos_client.get_season_videos(params.show_id, params.season),
        _get_show_title(params.show_id),
    )

    if isinstance(videos, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_videos",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=videos,
            operation="fetch_season_videos",
        )

    season_title = f"{title} - Season {params.season}"
    return VideoFormatters.format_videos_list(
        videos, season_title, embed_markdown, validate_input=False
    )


@handle_api_errors_func
async def fetch_season_watching(show_id: str, season: int) -> str:
    """Fetch users currently watching a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)

    Returns:
        Formatted markdown with user list
    """
    params = SeasonIdParam(show_id=show_id, season=season)

    watching_client = SeasonWatchingClient()
    show_title, users = await asyncio.gather(
        _get_show_title(params.show_id),
        watching_client.get_season_watching(params.show_id, params.season),
    )

    if isinstance(users, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_watching",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=users,
            operation="fetch_season_watching",
            show_title=show_title,
        )

    return SeasonFormatters.format_season_watching(users, show_title, params.season)


@handle_api_errors_func
async def fetch_season_translations(
    show_id: str, season: int, language: str = "all"
) -> str:
    """Fetch translations for a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        language: 2-character language code or 'all'

    Returns:
        Formatted markdown with translations
    """
    params = SeasonIdParam(show_id=show_id, season=season)

    try:
        language = validate_language(language)
    except ValueError as err:
        raise BaseToolErrorMixin.handle_validation_error(
            INVALID_LANGUAGE_MSG,
            parameter="language",
            provided_value=language,
        ) from err

    translations_client = SeasonTranslationsClient()
    show_title, translations = await asyncio.gather(
        _get_show_title(params.show_id),
        translations_client.get_season_translations(
            params.show_id, params.season, language
        ),
    )

    if isinstance(translations, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_translations",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=translations,
            operation="fetch_season_translations",
            show_title=show_title,
        )

    return SeasonFormatters.format_season_translations(
        translations, show_title, params.season
    )


@handle_api_errors_func
async def fetch_season_lists(
    show_id: str,
    season: int,
    list_type: Literal["all", "personal", "official", "watchlists"] = "all",
    sort: Literal[
        "popular", "likes", "comments", "items", "added", "updated"
    ] = "popular",
) -> str:
    """Fetch lists containing a specific season.

    Args:
        show_id: Trakt ID, slug, or IMDB ID
        season: Season number (0 for specials)
        list_type: Filter by type: 'all', 'personal', 'official', 'watchlists'
        sort: Sort order: 'popular', 'likes', 'comments', 'items', 'added', 'updated'

    Returns:
        Formatted markdown with lists
    """
    params = SeasonIdParam(show_id=show_id, season=season)

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

    lists_client = SeasonListsClient()
    show_title, lists = await asyncio.gather(
        _get_show_title(params.show_id),
        lists_client.get_season_lists(params.show_id, params.season, list_type, sort),
    )

    if isinstance(lists, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="season_lists",
            resource_id=f"{params.show_id}/S{params.season:02d}",
            error_message=lists,
            operation="fetch_season_lists",
            show_title=show_title,
        )

    return SeasonFormatters.format_season_lists(lists, show_title, params.season)


def register_season_tools(mcp: FastMCP) -> tuple[ToolHandler, ...]:
    """Register season tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_info"],
        description=(
            "Fetch detailed information about a specific TV show season, "
            "including episode count, ratings, and air dates."
        ),
    )
    async def fetch_season_info_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
    ) -> str:
        return await fetch_season_info(show_id, season)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_episodes"],
        description=(
            "Fetch all episodes for a specific TV show season "
            "with titles, ratings, and runtime."
        ),
    )
    async def fetch_season_episodes_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
    ) -> str:
        return await fetch_season_episodes(show_id, season)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_ratings"],
        description=(
            "Fetch ratings and voting statistics for a specific TV show season."
        ),
    )
    async def fetch_season_ratings_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
    ) -> str:
        return await fetch_season_ratings(show_id, season)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_stats"],
        description=(
            "Fetch engagement statistics for a specific TV show season "
            "including watchers, plays, collectors, and comments."
        ),
    )
    async def fetch_season_stats_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
    ) -> str:
        return await fetch_season_stats(show_id, season)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_people"],
        description=(
            "Fetch cast and crew for a specific TV show season, "
            "including character names and episode counts."
        ),
    )
    async def fetch_season_people_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
    ) -> str:
        return await fetch_season_people(show_id, season)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_videos"],
        description=(
            "Fetch videos (trailers, recaps, etc.) for a specific TV show season. "
            "Set embed_markdown=False for simple links."
        ),
    )
    async def fetch_season_videos_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        embed_markdown: Annotated[
            bool,
            Field(description=EMBED_MARKDOWN_DESCRIPTION),
        ] = True,
    ) -> str:
        return await fetch_season_videos(show_id, season, embed_markdown)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_watching"],
        description=(
            "Fetch users currently watching a specific TV show season right now."
        ),
    )
    async def fetch_season_watching_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
    ) -> str:
        return await fetch_season_watching(show_id, season)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_translations"],
        description=(
            "Fetch translations for a specific TV show season in different languages."
        ),
    )
    async def fetch_season_translations_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        language: Annotated[str, Field(description=LANGUAGE_DESCRIPTION)] = "all",
    ) -> str:
        return await fetch_season_translations(show_id, season, language)

    @mcp.tool(
        name=TOOL_NAMES["fetch_season_lists"],
        description="Fetch lists that contain a specific TV show season.",
    )
    async def fetch_season_lists_tool(
        show_id: Annotated[str, Field(min_length=1, description=SHOW_ID_DESCRIPTION)],
        season: Annotated[int, Field(ge=0, description=SEASON_DESCRIPTION)],
        list_type: Annotated[
            Literal["all", "personal", "official", "watchlists"],
            Field(description=LIST_TYPE_DESCRIPTION),
        ] = "all",
        sort: Annotated[
            Literal["popular", "likes", "comments", "items", "added", "updated"],
            Field(description=LIST_SORT_DESCRIPTION),
        ] = "popular",
    ) -> str:
        return await fetch_season_lists(show_id, season, list_type, sort)

    return (
        fetch_season_info_tool,
        fetch_season_episodes_tool,
        fetch_season_ratings_tool,
        fetch_season_stats_tool,
        fetch_season_people_tool,
        fetch_season_videos_tool,
        fetch_season_watching_tool,
        fetch_season_translations_tool,
        fetch_season_lists_tool,
    )
