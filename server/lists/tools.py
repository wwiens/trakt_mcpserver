"""Lists tools for the Trakt MCP server."""

import logging
from collections.abc import Awaitable, Callable
from typing import Annotated, Final, Literal, TypeAlias

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from client.lists import ListsClient
from client.pool import get_client
from config.api import DEFAULT_LIMIT
from config.mcp.descriptions import (
    LIMIT_DESCRIPTION,
    LIST_ID_DESCRIPTION,
    LIST_ITEM_TYPE_DESCRIPTION,
    LIST_OWNER_DESCRIPTION,
    PAGE_DESCRIPTION,
)
from models.formatters.lists import ListsFormatters
from server.base import LimitOnly, ToolErrors
from utils.api.errors import handle_api_errors_func
from utils.api.request_context import set_tool_context
from utils.validators import StrippedStr

logger: Final = logging.getLogger("trakt_mcp")

# Type alias for tool handlers
ToolHandler: TypeAlias = Callable[..., Awaitable[str]]


class ListItemsParams(BaseModel):
    """Parameters for tools that require a list owner and list ID."""

    list_owner: StrippedStr = Field(
        ...,
        min_length=1,
        description=LIST_OWNER_DESCRIPTION,
    )
    list_id: StrippedStr = Field(
        ...,
        min_length=1,
        description=LIST_ID_DESCRIPTION,
    )


@handle_api_errors_func
async def fetch_list_items(
    list_owner: str,
    list_id: str,
    item_type: Literal[
        "all", "movies", "shows", "seasons", "episodes", "people"
    ] = "all",
) -> str:
    """Fetch the items on a user's list.

    Args:
        list_owner: Trakt username (slug) that owns the list
        list_id: Trakt list ID or slug
        item_type: Filter by type: 'all', 'movies', 'shows', 'seasons',
            'episodes', 'people'

    Returns:
        Formatted markdown with the list's items
    """
    params = ListItemsParams(list_owner=list_owner, list_id=list_id)
    set_tool_context("list", params.list_id)

    client = get_client(ListsClient)
    items = await client.get_list_items(
        params.list_owner, params.list_id, item_type=item_type
    )

    if isinstance(items, str):
        raise ToolErrors.handle_api_string_error(
            resource_type="list_items",
            resource_id=params.list_id,
            error_message=items,
            operation="fetch_list_items",
            list_owner=params.list_owner,
        )

    context = f"{params.list_owner}/{params.list_id}"
    return ListsFormatters.format_list_items(items, context)


@handle_api_errors_func
async def fetch_trending_lists(
    limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Fetch trending lists from Trakt.

    Args:
        limit: Maximum lists to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        page: Page number. If None, auto-paginates up to 'limit' total lists.
            If specified, returns that page with pagination metadata.

    Returns:
        Information about trending lists.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = LimitOnly(limit=limit, page=page)
    limit, page = params.limit, params.page

    client = get_client(ListsClient)
    lists = await client.get_trending_lists(limit=limit, page=page)
    if isinstance(lists, str):
        raise ToolErrors.handle_api_string_error(
            resource_type="trending_lists",
            resource_id="list",
            error_message=lists,
            operation="fetch_trending_lists",
        )
    return ListsFormatters.format_trending_lists(lists)


@handle_api_errors_func
async def fetch_popular_lists(
    limit: int = DEFAULT_LIMIT, page: int | None = None
) -> str:
    """Fetch popular lists from Trakt.

    Args:
        limit: Maximum lists to return (default: 10, 0=fetch all). When page is
            None, this caps total results. When page is specified, this is per page.
        page: Page number. If None, auto-paginates up to 'limit' total lists.
            If specified, returns that page with pagination metadata.

    Returns:
        Information about popular lists.
    """
    # Validate parameters with Pydantic for normalization and constraints
    params = LimitOnly(limit=limit, page=page)
    limit, page = params.limit, params.page

    client = get_client(ListsClient)
    lists = await client.get_popular_lists(limit=limit, page=page)
    if isinstance(lists, str):
        raise ToolErrors.handle_api_string_error(
            resource_type="popular_lists",
            resource_id="list",
            error_message=lists,
            operation="fetch_popular_lists",
        )
    return ListsFormatters.format_popular_lists(lists)


def register_lists_tools(
    mcp: FastMCP,
) -> tuple[ToolHandler, ...]:
    """Register lists tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name="fetch_list_items",
        description=(
            "Get the items on a Trakt user's list. "
            "Returns movies, shows, and other items on a personal or "
            "official list, optionally filtered by type."
        ),
    )
    async def fetch_list_items_tool(
        list_owner: Annotated[
            str,
            Field(min_length=1, description=LIST_OWNER_DESCRIPTION),
        ],
        list_id: Annotated[
            str,
            Field(min_length=1, description=LIST_ID_DESCRIPTION),
        ],
        item_type: Annotated[
            Literal["all", "movies", "shows", "seasons", "episodes", "people"],
            Field(description=LIST_ITEM_TYPE_DESCRIPTION),
        ] = "all",
    ) -> str:
        return await fetch_list_items(list_owner, list_id, item_type)

    @mcp.tool(
        name="fetch_trending_lists",
        description=(
            "Get trending lists from Trakt. "
            "Returns the most-active community lists right now, ranked "
            "by recent likes and comments."
        ),
    )
    async def fetch_trending_lists_tool(
        limit: Annotated[int, Field(description=LIMIT_DESCRIPTION)] = DEFAULT_LIMIT,
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await fetch_trending_lists(limit, page)

    @mcp.tool(
        name="fetch_popular_lists",
        description=(
            "Get popular lists from Trakt. "
            "Returns community lists with the most likes and comments "
            "all-time."
        ),
    )
    async def fetch_popular_lists_tool(
        limit: Annotated[int, Field(description=LIMIT_DESCRIPTION)] = DEFAULT_LIMIT,
        page: Annotated[int | None, Field(description=PAGE_DESCRIPTION)] = None,
    ) -> str:
        return await fetch_popular_lists(limit, page)

    return (
        fetch_list_items_tool,
        fetch_trending_lists_tool,
        fetch_popular_lists_tool,
    )
