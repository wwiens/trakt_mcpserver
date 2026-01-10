"""Sync tools for the Trakt MCP server."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any, ClassVar, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from client.sync.client import SyncClient
from config.api import DEFAULT_LIMIT
from config.mcp.tools.sync import SYNC_TOOLS
from models.formatters.sync_ratings import SyncRatingsFormatters
from models.formatters.sync_watchlist import SyncWatchlistFormatters
from models.sync.ratings import (
    SyncRatingsSummary,
    TraktSyncRating,
    TraktSyncRatingItem,
    TraktSyncRatingsRequest,
)
from models.sync.watchlist import (
    SyncWatchlistSummary,
    TraktSyncWatchlistItem,
    TraktSyncWatchlistRequest,
    TraktWatchlistItem,
)
from models.types.pagination import PaginatedResponse, PaginationParams
from server.base import BaseToolErrorMixin, IdentifierValidatorMixin
from utils.api.errors import MCPError, handle_api_errors_func

logger = logging.getLogger("trakt_mcp")

WatchlistSortField = Literal[
    "rank",
    "added",
    "title",
    "released",
    "runtime",
    "popularity",
    "percentage",
    "votes",
]

# Type alias for tool handlers
ToolHandler = Callable[..., Awaitable[str]]


# Pydantic models for parameter validation
class UserRatingsParams(BaseModel):
    """Parameters for fetching user ratings."""

    rating_type: Literal["movies", "shows", "seasons", "episodes"] = "movies"
    rating: int | None = Field(
        default=None, ge=1, le=10, description="Optional specific rating to filter by"
    )
    page: int | None = Field(
        default=None, ge=1, description="Optional page number for pagination (1-based)"
    )

    @field_validator("rating", mode="before")
    @classmethod
    def _validate_rating(cls, v: object) -> object:
        if v is None or v == "":
            return None
        return v

    @field_validator("page", mode="before")
    @classmethod
    def _validate_page(cls, v: object) -> object:
        if v is None or v == "":
            return None
        return v


class UserRatingRequestItem(IdentifierValidatorMixin):
    """Single rating item for add/remove operations."""

    _identifier_error_prefix: ClassVar[str] = "Rating item"

    rating: int = Field(ge=1, le=10, description="Rating from 1 to 10")


class UserRatingIdentifier(IdentifierValidatorMixin):
    """Rating item identifier for removal operations (no rating required)."""

    _identifier_error_prefix: ClassVar[str] = "Rating item"


class UserRatingRequest(BaseModel):
    """Parameters for adding/removing user ratings."""

    rating_type: Literal["movies", "shows", "seasons", "episodes"]
    items: list[UserRatingRequestItem] = Field(
        min_length=1, description="List of items to rate"
    )


class UserWatchlistParams(BaseModel):
    """Parameters for fetching user watchlist."""

    watchlist_type: Literal["all", "movies", "shows", "seasons", "episodes"] = "all"
    sort_by: WatchlistSortField = "rank"
    sort_how: Literal["asc", "desc"] = "asc"
    page: int | None = Field(
        default=None, ge=1, description="Optional page number for pagination (1-based)"
    )

    @field_validator("page", mode="before")
    @classmethod
    def _validate_page(cls, v: object) -> object:
        if v is None or v == "":
            return None
        return v


class UserWatchlistRequestItem(IdentifierValidatorMixin):
    """Single watchlist item for add operations (with optional notes)."""

    _identifier_error_prefix: ClassVar[str] = "Watchlist item"

    notes: str | None = Field(
        default=None,
        max_length=500,
        description="Optional notes (VIP only, 500 char max)",
    )

    @field_validator("notes", mode="before")
    @classmethod
    def _strip_notes(cls, v: object) -> object:
        """Strip whitespace from notes field."""
        return v.strip() if isinstance(v, str) else v


class UserWatchlistIdentifier(IdentifierValidatorMixin):
    """Watchlist item identifier for removal operations (no notes)."""

    _identifier_error_prefix: ClassVar[str] = "Watchlist item"


class UserWatchlistRequest(BaseModel):
    """Parameters for adding/removing user watchlist items."""

    watchlist_type: Literal["movies", "shows", "seasons", "episodes"]
    items: list[UserWatchlistRequestItem] = Field(
        min_length=1, description="List of items to add to watchlist"
    )


@handle_api_errors_func
async def fetch_user_ratings(
    rating_type: Literal["movies", "shows", "seasons", "episodes"] = "movies",
    rating: int | None = None,
    page: int | None = None,
) -> str:
    """Fetch authenticated user's personal ratings from Trakt.

    Args:
        rating_type: Type of ratings to fetch (movies, shows, seasons, episodes)
        rating: Optional specific rating to filter by (1-10)
        page: Optional page number for pagination (1-based)

    Returns:
        User's personal ratings formatted as markdown. When 'page' is None,
        only the first page is retrieved (see pagination info in the output).

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("fetch_user_ratings called with rating_type=%s", rating_type)
    # Validate parameters with Pydantic
    params = UserRatingsParams(rating_type=rating_type, rating=rating, page=page)
    rating_type, rating, page = params.rating_type, params.rating, params.page

    try:
        client = SyncClient()

        # If 'page' is provided, request that page; otherwise use default page=1.
        pagination_params = (
            PaginationParams(page=page, limit=DEFAULT_LIMIT)
            if page is not None
            else None
        )
        paginated_result: PaginatedResponse[
            TraktSyncRating
        ] = await client.get_sync_ratings(
            rating_type, rating, pagination=pagination_params
        )

        # Handle transitional case where API returns error strings
        if isinstance(paginated_result, str):
            error = BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"user_{rating_type}_ratings",
                resource_id=f"user_ratings_{rating_type}",
                error_message=paginated_result,
                operation="fetch_user_ratings",
            )
            raise error

        return SyncRatingsFormatters.format_user_ratings(
            paginated_result, rating_type, rating
        )
    except MCPError:
        raise


@handle_api_errors_func
async def add_user_ratings(
    rating_type: Literal["movies", "shows", "seasons", "episodes"],
    items: list[UserRatingRequestItem],
) -> str:
    """Add new ratings for the authenticated user.

    Args:
        rating_type: Type of content to rate (movies, shows, seasons, episodes)
        items: List of items to rate with rating and identification info

    Returns:
        Summary of added ratings with counts

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("add_user_ratings called with rating_type=%s", rating_type)

    try:
        client = SyncClient()

        # Convert to sync request format
        sync_items: list[TraktSyncRatingItem] = []
        for item in items:
            # Create sync rating item
            sync_item_data: dict[str, Any] = {
                "rating": item.rating,
                "ids": item.build_ids_dict(),
            }

            # Add title and year if provided
            if item.title:
                sync_item_data["title"] = item.title
            if item.year:
                sync_item_data["year"] = item.year

            sync_items.append(TraktSyncRatingItem(**sync_item_data))

        # Create request with the appropriate type
        request_data: dict[str, Any] = {rating_type: sync_items}
        request = TraktSyncRatingsRequest(**request_data)

        summary: SyncRatingsSummary = await client.add_sync_ratings(request)

        # Handle transitional case where API returns error strings
        if isinstance(summary, str):
            error = BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"add_user_{rating_type}_ratings",
                resource_id=f"add_ratings_{rating_type}",
                error_message=summary,
                operation="add_user_ratings",
            )
            raise error

        return SyncRatingsFormatters.format_user_ratings_summary(
            summary, "added", rating_type
        )
    except MCPError:
        raise


@handle_api_errors_func
async def remove_user_ratings(
    rating_type: Literal["movies", "shows", "seasons", "episodes"],
    items: list[UserRatingIdentifier],
) -> str:
    """Remove ratings for the authenticated user.

    Args:
        rating_type: Type of content to unrate (movies, shows, seasons, episodes)
        items: List of items to remove ratings from (no rating values needed, just identification)

    Returns:
        Summary of removed ratings with counts

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("remove_user_ratings called with rating_type=%s", rating_type)

    try:
        client = SyncClient()

        # Convert to sync request format (no ratings needed for removal)
        sync_items: list[TraktSyncRatingItem] = []
        for item in items:
            # Create sync rating item (no rating for removal)
            sync_item_data: dict[str, Any] = {"ids": item.build_ids_dict()}

            # Add title and year if provided
            if item.title:
                sync_item_data["title"] = item.title
            if item.year:
                sync_item_data["year"] = item.year

            sync_items.append(TraktSyncRatingItem(**sync_item_data))

        # Create request with the appropriate type
        request_data: dict[str, Any] = {rating_type: sync_items}
        request = TraktSyncRatingsRequest(**request_data)

        summary: SyncRatingsSummary = await client.remove_sync_ratings(request)

        # Handle transitional case where API returns error strings
        if isinstance(summary, str):
            error = BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"remove_user_{rating_type}_ratings",
                resource_id=f"remove_ratings_{rating_type}",
                error_message=summary,
                operation="remove_user_ratings",
            )
            raise error

        return SyncRatingsFormatters.format_user_ratings_summary(
            summary, "removed", rating_type
        )
    except MCPError:
        raise


@handle_api_errors_func
async def fetch_user_watchlist(
    watchlist_type: Literal["all", "movies", "shows", "seasons", "episodes"] = "all",
    sort_by: WatchlistSortField = "rank",
    sort_how: Literal["asc", "desc"] = "asc",
    page: int | None = None,
) -> str:
    """Fetch authenticated user's watchlist from Trakt.

    Args:
        watchlist_type: Type of watchlist items to fetch (all, movies, shows, seasons, episodes)
        sort_by: Field to sort by (rank, added, title, released, runtime, etc.)
        sort_how: Sort direction (asc, desc)
        page: Optional page number for pagination (1-based)

    Returns:
        User's watchlist formatted as markdown. When 'page' is None,
        only the first page is retrieved (see pagination info in the output).

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("fetch_user_watchlist called with watchlist_type=%s", watchlist_type)
    # Validate parameters with Pydantic
    params = UserWatchlistParams(
        watchlist_type=watchlist_type, sort_by=sort_by, sort_how=sort_how, page=page
    )
    watchlist_type, sort_by, sort_how, page = (
        params.watchlist_type,
        params.sort_by,
        params.sort_how,
        params.page,
    )

    try:
        client = SyncClient()

        # If 'page' is provided, request that page; otherwise use default page=1.
        pagination_params = (
            PaginationParams(page=page, limit=DEFAULT_LIMIT)
            if page is not None
            else None
        )
        paginated_result: PaginatedResponse[
            TraktWatchlistItem
        ] = await client.get_sync_watchlist(
            watchlist_type, sort_by, sort_how, pagination=pagination_params
        )

        # Handle transitional case where API returns error strings
        if isinstance(paginated_result, str):
            error = BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"user_{watchlist_type}_watchlist",
                resource_id=f"user_watchlist_{watchlist_type}",
                error_message=paginated_result,
                operation="fetch_user_watchlist",
            )
            raise error

        return SyncWatchlistFormatters.format_user_watchlist(
            paginated_result, watchlist_type, sort_by, sort_how
        )
    except MCPError:
        raise


@handle_api_errors_func
async def add_user_watchlist(
    watchlist_type: Literal["movies", "shows", "seasons", "episodes"],
    items: list[UserWatchlistRequestItem],
) -> str:
    """Add items to the authenticated user's watchlist.

    Args:
        watchlist_type: Type of content to add (movies, shows, seasons, episodes)
        items: List of items to add with identification info and optional notes (VIP only)

    Returns:
        Summary of added watchlist items with counts

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("add_user_watchlist called with watchlist_type=%s", watchlist_type)

    try:
        client = SyncClient()

        # Convert to sync request format
        sync_items: list[TraktSyncWatchlistItem] = []
        for item in items:
            # Create sync watchlist item
            sync_item_data: dict[str, Any] = {"ids": item.build_ids_dict()}

            # Add title and year if provided
            if item.title:
                sync_item_data["title"] = item.title
            if item.year:
                sync_item_data["year"] = item.year
            # Add notes if provided (VIP only)
            if item.notes:
                sync_item_data["notes"] = item.notes

            sync_items.append(TraktSyncWatchlistItem(**sync_item_data))

        # Create request with the appropriate type
        request_data: dict[str, Any] = {watchlist_type: sync_items}
        request = TraktSyncWatchlistRequest(**request_data)

        summary: SyncWatchlistSummary = await client.add_sync_watchlist(request)

        # Handle transitional case where API returns error strings
        if isinstance(summary, str):
            error = BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"add_user_{watchlist_type}_watchlist",
                resource_id=f"add_watchlist_{watchlist_type}",
                error_message=summary,
                operation="add_user_watchlist",
            )
            raise error

        return SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, "added", watchlist_type
        )
    except MCPError:
        raise


@handle_api_errors_func
async def remove_user_watchlist(
    watchlist_type: Literal["movies", "shows", "seasons", "episodes"],
    items: list[UserWatchlistIdentifier],
) -> str:
    """Remove items from the authenticated user's watchlist.

    Args:
        watchlist_type: Type of content to remove (movies, shows, seasons, episodes)
        items: List of items to remove from watchlist (no notes needed, just identification)

    Returns:
        Summary of removed watchlist items with counts

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("remove_user_watchlist called with watchlist_type=%s", watchlist_type)

    try:
        client = SyncClient()

        # Convert to sync request format (no notes for removal)
        sync_items: list[TraktSyncWatchlistItem] = []
        for item in items:
            # Create sync watchlist item (no notes for removal)
            sync_item_data: dict[str, Any] = {"ids": item.build_ids_dict()}

            # Add title and year if provided
            if item.title:
                sync_item_data["title"] = item.title
            if item.year:
                sync_item_data["year"] = item.year

            sync_items.append(TraktSyncWatchlistItem(**sync_item_data))

        # Create request with the appropriate type
        request_data: dict[str, Any] = {watchlist_type: sync_items}
        request = TraktSyncWatchlistRequest(**request_data)

        summary: SyncWatchlistSummary = await client.remove_sync_watchlist(request)

        # Handle transitional case where API returns error strings
        if isinstance(summary, str):
            error = BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"remove_user_{watchlist_type}_watchlist",
                resource_id=f"remove_watchlist_{watchlist_type}",
                error_message=summary,
                operation="remove_user_watchlist",
            )
            raise error

        return SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, "removed", watchlist_type
        )
    except MCPError:
        raise


def register_sync_tools(
    mcp: FastMCP,
) -> tuple[
    ToolHandler, ToolHandler, ToolHandler, ToolHandler, ToolHandler, ToolHandler
]:
    """Register sync rating and watchlist tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=SYNC_TOOLS["fetch_user_ratings"],
        description=(
            "Fetch the authenticated user's personal ratings from Trakt. "
            "Supports optional pagination with 'page' parameter. "
            "Requires OAuth authentication."
        ),
    )
    async def fetch_user_ratings_tool(
        rating_type: Literal["movies", "shows", "seasons", "episodes"] = "movies",
        rating: int | None = None,
        page: int | None = None,
    ) -> str:
        # Validate parameters with Pydantic
        params = UserRatingsParams(rating_type=rating_type, rating=rating, page=page)
        return await fetch_user_ratings(params.rating_type, params.rating, params.page)

    @mcp.tool(
        name=SYNC_TOOLS["add_user_ratings"],
        description="Add new ratings for the authenticated user. Requires OAuth authentication.",
    )
    async def add_user_ratings_tool(
        rating_type: Literal["movies", "shows", "seasons", "episodes"],
        items: list[UserRatingRequestItem],
    ) -> str:
        return await add_user_ratings(rating_type, items)

    @mcp.tool(
        name=SYNC_TOOLS["remove_user_ratings"],
        description="Remove ratings for the authenticated user. Requires OAuth authentication.",
    )
    async def remove_user_ratings_tool(
        rating_type: Literal["movies", "shows", "seasons", "episodes"],
        items: list[UserRatingIdentifier],
    ) -> str:
        return await remove_user_ratings(rating_type, items)

    @mcp.tool(
        name=SYNC_TOOLS["fetch_user_watchlist"],
        description=(
            "Fetch the authenticated user's watchlist from Trakt. "
            "Supports optional pagination with 'page' parameter and sorting options. "
            "Requires OAuth authentication."
        ),
    )
    async def fetch_user_watchlist_tool(
        watchlist_type: Literal[
            "all", "movies", "shows", "seasons", "episodes"
        ] = "all",
        sort_by: WatchlistSortField = "rank",
        sort_how: Literal["asc", "desc"] = "asc",
        page: int | None = None,
    ) -> str:
        # Validate parameters with Pydantic
        params = UserWatchlistParams(
            watchlist_type=watchlist_type, sort_by=sort_by, sort_how=sort_how, page=page
        )
        return await fetch_user_watchlist(
            params.watchlist_type, params.sort_by, params.sort_how, params.page
        )

    @mcp.tool(
        name=SYNC_TOOLS["add_user_watchlist"],
        description=(
            "Add items to the authenticated user's watchlist. "
            "Supports optional notes (VIP only, 500 character limit). "
            "Requires OAuth authentication."
        ),
    )
    async def add_user_watchlist_tool(
        watchlist_type: Literal["movies", "shows", "seasons", "episodes"],
        items: list[UserWatchlistRequestItem],
    ) -> str:
        return await add_user_watchlist(watchlist_type, items)

    @mcp.tool(
        name=SYNC_TOOLS["remove_user_watchlist"],
        description=(
            "Remove items from the authenticated user's watchlist. "
            "Requires OAuth authentication."
        ),
    )
    async def remove_user_watchlist_tool(
        watchlist_type: Literal["movies", "shows", "seasons", "episodes"],
        items: list[UserWatchlistIdentifier],
    ) -> str:
        return await remove_user_watchlist(watchlist_type, items)

    # Return handlers for type checker visibility
    return (
        fetch_user_ratings_tool,
        add_user_ratings_tool,
        remove_user_ratings_tool,
        fetch_user_watchlist_tool,
        add_user_watchlist_tool,
        remove_user_watchlist_tool,
    )
