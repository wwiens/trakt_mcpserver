"""People tools for the Trakt MCP server."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal, TypeAlias

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from client.people.lists import PersonListsClient
from client.people.movies import PersonMoviesClient
from client.people.shows import PersonShowsClient
from client.people.summary import PersonSummaryClient
from config.mcp.descriptions import (
    EXTENDED_DESCRIPTION,
    LIST_SORT_DESCRIPTION,
    LIST_TYPE_DESCRIPTION,
    PERSON_ID_DESCRIPTION,
)
from config.mcp.tools import TOOL_NAMES
from models.formatters.people import PeopleFormatters
from server.base import BaseToolErrorMixin
from utils.api.errors import handle_api_errors_func

logger = logging.getLogger("trakt_mcp")

# Type alias for tool handlers
ToolHandler: TypeAlias = Callable[..., Awaitable[str]]


class PersonIdParam(BaseModel):
    """Parameters for tools that require a person ID."""

    person_id: str = Field(
        ...,
        min_length=1,
        description=PERSON_ID_DESCRIPTION,
    )

    @field_validator("person_id", mode="before")
    @classmethod
    def _strip_person_id(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


async def _get_person_name(person_id: str) -> str:
    """Fetch the person name for use in formatted responses.

    Falls back to ``Person ID: <person_id>`` when the lookup fails
    for any reason so callers always receive a usable name string.

    Args:
        person_id: Trakt ID, slug, or IMDB ID

    Returns:
        Person name string, or fallback on failure
    """
    try:
        client = PersonSummaryClient()
        person_data = await client.get_person(person_id)

        if isinstance(person_data, str):
            return f"Person ID: {person_id}"

        return person_data.get("name", f"Person ID: {person_id}")
    except Exception as exc:  # Intentional broad fallback per docstring
        logger.debug(
            "Non-fatal exception during person name lookup; falling back to ID.",
            exc_info=True,
            extra={
                "resource_id": person_id,
                "operation": "fetch_person_name",
                "error": str(exc),
            },
        )
        return f"Person ID: {person_id}"


@handle_api_errors_func
async def fetch_person_summary(person_id: str, extended: bool = True) -> str:
    """Fetch details for a specific person.

    Args:
        person_id: Trakt ID, slug, or IMDB ID
        extended: Return full biographical data or just name/IDs

    Returns:
        Formatted markdown with person details
    """
    params = PersonIdParam(person_id=person_id)

    client = PersonSummaryClient()
    if extended:
        person = await client.get_person_extended(params.person_id)
    else:
        person = await client.get_person(params.person_id)

    if isinstance(person, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="person",
            resource_id=params.person_id,
            error_message=person,
            operation="fetch_person_summary",
        )

    return PeopleFormatters.format_person_summary(person)


@handle_api_errors_func
async def fetch_person_movies(person_id: str) -> str:
    """Fetch movie credits for a specific person.

    Args:
        person_id: Trakt ID, slug, or IMDB ID

    Returns:
        Formatted markdown with movie credits
    """
    params = PersonIdParam(person_id=person_id)

    movies_client = PersonMoviesClient()
    person_name, movie_credits = await asyncio.gather(
        _get_person_name(params.person_id),
        movies_client.get_person_movies(params.person_id),
    )

    if isinstance(movie_credits, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="person_movies",
            resource_id=params.person_id,
            error_message=movie_credits,
            operation="fetch_person_movies",
            person_name=person_name,
        )

    return PeopleFormatters.format_person_movie_credits(movie_credits, person_name)


@handle_api_errors_func
async def fetch_person_shows(person_id: str) -> str:
    """Fetch show credits for a specific person.

    Args:
        person_id: Trakt ID, slug, or IMDB ID

    Returns:
        Formatted markdown with show credits
    """
    params = PersonIdParam(person_id=person_id)

    shows_client = PersonShowsClient()
    person_name, show_credits = await asyncio.gather(
        _get_person_name(params.person_id),
        shows_client.get_person_shows(params.person_id),
    )

    if isinstance(show_credits, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="person_shows",
            resource_id=params.person_id,
            error_message=show_credits,
            operation="fetch_person_shows",
            person_name=person_name,
        )

    return PeopleFormatters.format_person_show_credits(show_credits, person_name)


@handle_api_errors_func
async def fetch_person_lists(
    person_id: str,
    list_type: Literal["all", "personal", "official", "watchlists"] = "all",
    sort: Literal[
        "popular", "likes", "comments", "items", "added", "updated"
    ] = "popular",
) -> str:
    """Fetch lists containing a specific person.

    Args:
        person_id: Trakt ID, slug, or IMDB ID
        list_type: List type filter (all, personal, official, watchlists)
        sort: Sort order (popular, likes, comments, items, added, updated)

    Returns:
        Formatted markdown with lists
    """
    params = PersonIdParam(person_id=person_id)

    lists_client = PersonListsClient()
    person_name, lists = await asyncio.gather(
        _get_person_name(params.person_id),
        lists_client.get_person_lists(params.person_id, list_type=list_type, sort=sort),
    )

    if isinstance(lists, str):
        raise BaseToolErrorMixin.handle_api_string_error(
            resource_type="person_lists",
            resource_id=params.person_id,
            error_message=lists,
            operation="fetch_person_lists",
            person_name=person_name,
        )

    return PeopleFormatters.format_person_lists(lists, person_name)


def register_people_tools(
    mcp: FastMCP,
) -> tuple[ToolHandler, ...]:
    """Register people tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=TOOL_NAMES["fetch_person_summary"],
        description=(
            "Get person details from Trakt. "
            "Default (extended=true): full biographical data including "
            "birthday, biography, social media. "
            "Basic (extended=false): name and IDs only."
        ),
    )
    async def fetch_person_summary_tool(
        person_id: Annotated[
            str,
            Field(min_length=1, description=PERSON_ID_DESCRIPTION),
        ],
        extended: Annotated[bool, Field(description=EXTENDED_DESCRIPTION)] = True,
    ) -> str:
        return await fetch_person_summary(person_id, extended)

    @mcp.tool(
        name=TOOL_NAMES["fetch_person_movies"],
        description=(
            "Get all movie credits for a person from Trakt. "
            "Returns cast roles and crew positions grouped by "
            "department."
        ),
    )
    async def fetch_person_movies_tool(
        person_id: Annotated[
            str,
            Field(min_length=1, description=PERSON_ID_DESCRIPTION),
        ],
    ) -> str:
        return await fetch_person_movies(person_id)

    @mcp.tool(
        name=TOOL_NAMES["fetch_person_shows"],
        description=(
            "Get all show credits for a person from Trakt. "
            "Returns cast roles with episode counts and crew "
            "positions grouped by department."
        ),
    )
    async def fetch_person_shows_tool(
        person_id: Annotated[
            str,
            Field(min_length=1, description=PERSON_ID_DESCRIPTION),
        ],
    ) -> str:
        return await fetch_person_shows(person_id)

    @mcp.tool(
        name=TOOL_NAMES["fetch_person_lists"],
        description=(
            "Get lists containing a specific person from Trakt. "
            "Returns personal or official lists sorted by "
            "popularity, likes, or other criteria."
        ),
    )
    async def fetch_person_lists_tool(
        person_id: Annotated[
            str,
            Field(min_length=1, description=PERSON_ID_DESCRIPTION),
        ],
        list_type: Annotated[
            Literal["all", "personal", "official", "watchlists"],
            Field(description=LIST_TYPE_DESCRIPTION),
        ] = "all",
        sort: Annotated[
            Literal["popular", "likes", "comments", "items", "added", "updated"],
            Field(description=LIST_SORT_DESCRIPTION),
        ] = "popular",
    ) -> str:
        return await fetch_person_lists(person_id, list_type, sort)

    return (
        fetch_person_summary_tool,
        fetch_person_movies_tool,
        fetch_person_shows_tool,
        fetch_person_lists_tool,
    )
