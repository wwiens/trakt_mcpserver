"""Sync tools for the Trakt MCP server."""

import logging
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, ClassVar, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from client.sync.client import SyncClient
from config.api import DEFAULT_LIMIT
from config.mcp.descriptions import (
    HISTORY_END_AT_DESCRIPTION,
    HISTORY_ITEM_ID_DESCRIPTION,
    HISTORY_ITEMS_DESCRIPTION,
    HISTORY_QUERY_TYPE_DESCRIPTION,
    HISTORY_REMOVE_ITEMS_DESCRIPTION,
    HISTORY_START_AT_DESCRIPTION,
    HISTORY_TYPE_DESCRIPTION,
    PAGE_DESCRIPTION,
    RATING_FILTER_DESCRIPTION,
    RATING_ITEMS_DESCRIPTION,
    RATING_REMOVE_ITEMS_DESCRIPTION,
    RATING_TYPE_DESCRIPTION,
    SORT_DIRECTION_DESCRIPTION,
    WATCHLIST_ITEMS_DESCRIPTION,
    WATCHLIST_REMOVE_ITEMS_DESCRIPTION,
    WATCHLIST_SORT_BY_DESCRIPTION,
    WATCHLIST_TYPE_DESCRIPTION,
    WATCHLIST_TYPE_REQUIRED_DESCRIPTION,
)
from config.mcp.tools.sync import SYNC_TOOLS
from models.formatters.sync_history import SyncHistoryFormatters
from models.formatters.sync_ratings import SyncRatingsFormatters
from models.formatters.sync_watchlist import SyncWatchlistFormatters
from models.sync.history import (
    HistorySummary,
    TraktHistoryItem,
    TraktHistoryRequest,
)
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


class HistoryRequestItem(IdentifierValidatorMixin):
    """Single history item for add operations."""

    _identifier_error_prefix: ClassVar[str] = "History item"

    watched_at: str | None = Field(
        default=None, description="ISO 8601 timestamp when watched"
    )


class HistoryRemoveItem(IdentifierValidatorMixin):
    """History item identifier for removal operations."""

    _identifier_error_prefix: ClassVar[str] = "History item"


@handle_api_errors_func
async def fetch_history(
    history_type: Literal["movies", "shows", "seasons", "episodes"] | None = None,
    item_id: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    page: int | None = None,
) -> str:
    """Fetch watch history, optionally filtered by type and/or specific item.

    Args:
        history_type: Type of content to filter (movies, shows, seasons, episodes)
        item_id: Trakt ID for a specific item (requires history_type)
        start_at: Filter watches after this date (ISO 8601)
        end_at: Filter watches before this date (ISO 8601)
        page: Page number for paginated results (1-based)

    Returns:
        Watch history formatted as markdown with pagination info

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("fetch_history called with type=%s, item_id=%s", history_type, item_id)

    client = SyncClient()

    # Create pagination params if page is specified
    pagination_params = (
        PaginationParams(page=page, limit=DEFAULT_LIMIT) if page is not None else None
    )

    result = await client.get_history(
        history_type=history_type,
        item_id=item_id,
        start_at=start_at,
        end_at=end_at,
        pagination=pagination_params,
    )

    # Handle transitional case where API returns error strings
    if isinstance(result, str):
        error = BaseToolErrorMixin.handle_api_string_error(
            resource_type="history",
            resource_id=item_id or "all",
            error_message=result,
            operation="fetch_history",
        )
        raise error

    return SyncHistoryFormatters.format_watch_history(result, history_type, item_id)


@handle_api_errors_func
async def add_to_history(
    history_type: Literal["movies", "shows", "seasons", "episodes"],
    items: list[HistoryRequestItem],
) -> str:
    """Add items to watch history.

    Args:
        history_type: Type of content to add (movies, shows, seasons, episodes)
        items: List of items to add with identification info and optional watched_at

    Returns:
        Summary of added history items with counts

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("add_to_history called with type=%s", history_type)

    client = SyncClient()

    # Convert to history request format
    history_items: list[TraktHistoryItem] = []
    for item in items:
        # Create history item
        item_data: dict[str, Any] = {"ids": item.build_ids_dict()}

        # Add title and year if provided
        if item.title:
            item_data["title"] = item.title
        if item.year:
            item_data["year"] = item.year
        # Add watched_at if provided
        if item.watched_at:
            item_data["watched_at"] = item.watched_at

        history_items.append(TraktHistoryItem(**item_data))

    # Create request with the appropriate type
    request_data: dict[str, Any] = {history_type: history_items}
    request = TraktHistoryRequest(**request_data)

    summary: HistorySummary = await client.add_to_history(request)

    # Handle transitional case where API returns error strings
    if isinstance(summary, str):
        error = BaseToolErrorMixin.handle_api_string_error(
            resource_type=f"add_history_{history_type}",
            resource_id=f"add_history_{history_type}",
            error_message=summary,
            operation="add_to_history",
        )
        raise error

    return SyncHistoryFormatters.format_history_summary(summary, "added", history_type)


@handle_api_errors_func
async def remove_from_history(
    history_type: Literal["movies", "shows", "seasons", "episodes"],
    items: list[HistoryRemoveItem],
) -> str:
    """Remove items from watch history.

    Args:
        history_type: Type of content to remove (movies, shows, seasons, episodes)
        items: List of items to remove with identification info

    Returns:
        Summary of removed history items with counts

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    logger.debug("remove_from_history called with type=%s", history_type)

    client = SyncClient()

    # Convert to history request format
    history_items: list[TraktHistoryItem] = []
    for item in items:
        # Create history item (no watched_at for removal)
        item_data: dict[str, Any] = {"ids": item.build_ids_dict()}

        # Add title and year if provided
        if item.title:
            item_data["title"] = item.title
        if item.year:
            item_data["year"] = item.year

        history_items.append(TraktHistoryItem(**item_data))

    # Create request with the appropriate type
    request_data: dict[str, Any] = {history_type: history_items}
    request = TraktHistoryRequest(**request_data)

    summary: HistorySummary = await client.remove_from_history(request)

    # Handle transitional case where API returns error strings
    if isinstance(summary, str):
        error = BaseToolErrorMixin.handle_api_string_error(
            resource_type=f"remove_history_{history_type}",
            resource_id=f"remove_history_{history_type}",
            error_message=summary,
            operation="remove_from_history",
        )
        raise error

    return SyncHistoryFormatters.format_history_summary(
        summary, "removed", history_type
    )


def register_sync_tools(
    mcp: FastMCP,
) -> tuple[
    ToolHandler,
    ToolHandler,
    ToolHandler,
    ToolHandler,
    ToolHandler,
    ToolHandler,
    ToolHandler,
    ToolHandler,
    ToolHandler,
]:
    """Register sync tools (ratings, watchlist, history) with the MCP server.

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
        rating_type: Annotated[
            Literal["movies", "shows", "seasons", "episodes"],
            Field(description=RATING_TYPE_DESCRIPTION),
        ] = "movies",
        rating: Annotated[
            int | None,
            Field(ge=1, le=10, description=RATING_FILTER_DESCRIPTION),
        ] = None,
        page: Annotated[
            int | None,
            Field(ge=1, description=PAGE_DESCRIPTION),
        ] = None,
    ) -> str:
        # Validate parameters with Pydantic
        params = UserRatingsParams(rating_type=rating_type, rating=rating, page=page)
        return await fetch_user_ratings(params.rating_type, params.rating, params.page)

    @mcp.tool(
        name=SYNC_TOOLS["add_user_ratings"],
        description="Add new ratings for the authenticated user. Requires OAuth authentication.",
    )
    async def add_user_ratings_tool(
        rating_type: Annotated[
            Literal["movies", "shows", "seasons", "episodes"],
            Field(description=RATING_TYPE_DESCRIPTION),
        ],
        items: Annotated[
            list[UserRatingRequestItem],
            Field(
                min_length=1,
                description=RATING_ITEMS_DESCRIPTION,
            ),
        ],
    ) -> str:
        return await add_user_ratings(rating_type, items)

    @mcp.tool(
        name=SYNC_TOOLS["remove_user_ratings"],
        description="Remove ratings for the authenticated user. Requires OAuth authentication.",
    )
    async def remove_user_ratings_tool(
        rating_type: Annotated[
            Literal["movies", "shows", "seasons", "episodes"],
            Field(description=RATING_TYPE_DESCRIPTION),
        ],
        items: Annotated[
            list[UserRatingIdentifier],
            Field(
                min_length=1,
                description=RATING_REMOVE_ITEMS_DESCRIPTION,
            ),
        ],
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
        watchlist_type: Annotated[
            Literal["all", "movies", "shows", "seasons", "episodes"],
            Field(description=WATCHLIST_TYPE_DESCRIPTION),
        ] = "all",
        sort_by: Annotated[
            WatchlistSortField,
            Field(description=WATCHLIST_SORT_BY_DESCRIPTION),
        ] = "rank",
        sort_how: Annotated[
            Literal["asc", "desc"],
            Field(description=SORT_DIRECTION_DESCRIPTION),
        ] = "asc",
        page: Annotated[
            int | None,
            Field(ge=1, description=PAGE_DESCRIPTION),
        ] = None,
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
        watchlist_type: Annotated[
            Literal["movies", "shows", "seasons", "episodes"],
            Field(description=WATCHLIST_TYPE_REQUIRED_DESCRIPTION),
        ],
        items: Annotated[
            list[UserWatchlistRequestItem],
            Field(
                min_length=1,
                description=WATCHLIST_ITEMS_DESCRIPTION,
            ),
        ],
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
        watchlist_type: Annotated[
            Literal["movies", "shows", "seasons", "episodes"],
            Field(description=WATCHLIST_TYPE_REQUIRED_DESCRIPTION),
        ],
        items: Annotated[
            list[UserWatchlistIdentifier],
            Field(
                min_length=1,
                description=WATCHLIST_REMOVE_ITEMS_DESCRIPTION,
            ),
        ],
    ) -> str:
        return await remove_user_watchlist(watchlist_type, items)

    @mcp.tool(
        name=SYNC_TOOLS["fetch_history"],
        description=(
            "Check if a movie or show has been watched, or browse watch history. "
            "For 'Have I seen [movie]?': provide history_type='movies' and item_id. "
            "Returns watch dates and count. Empty result means not watched. "
            "Supports optional pagination with 'page' parameter. "
            "Requires OAuth authentication."
        ),
    )
    async def fetch_history_tool(
        history_type: Annotated[
            Literal["movies", "shows", "seasons", "episodes"] | None,
            Field(description=HISTORY_QUERY_TYPE_DESCRIPTION),
        ] = None,
        item_id: Annotated[
            str | None,
            Field(description=HISTORY_ITEM_ID_DESCRIPTION),
        ] = None,
        start_at: Annotated[
            str | None,
            Field(description=HISTORY_START_AT_DESCRIPTION),
        ] = None,
        end_at: Annotated[
            str | None,
            Field(description=HISTORY_END_AT_DESCRIPTION),
        ] = None,
        page: Annotated[
            int | None,
            Field(ge=1, description=PAGE_DESCRIPTION),
        ] = None,
    ) -> str:
        return await fetch_history(history_type, item_id, start_at, end_at, page)

    @mcp.tool(
        name=SYNC_TOOLS["add_to_history"],
        description=(
            "Add items to watch history. Marks movies, shows, seasons, or episodes "
            "as watched. Optionally specify when they were watched. "
            "Requires OAuth authentication."
        ),
    )
    async def add_to_history_tool(
        history_type: Annotated[
            Literal["movies", "shows", "seasons", "episodes"],
            Field(description=HISTORY_TYPE_DESCRIPTION),
        ],
        items: Annotated[
            list[HistoryRequestItem],
            Field(min_length=1, description=HISTORY_ITEMS_DESCRIPTION),
        ],
    ) -> str:
        return await add_to_history(history_type, items)

    @mcp.tool(
        name=SYNC_TOOLS["remove_from_history"],
        description=(
            "Remove items from watch history. Removes movies, shows, seasons, "
            "or episodes from your watched history. "
            "Requires OAuth authentication."
        ),
    )
    async def remove_from_history_tool(
        history_type: Annotated[
            Literal["movies", "shows", "seasons", "episodes"],
            Field(description=HISTORY_TYPE_DESCRIPTION),
        ],
        items: Annotated[
            list[HistoryRemoveItem],
            Field(min_length=1, description=HISTORY_REMOVE_ITEMS_DESCRIPTION),
        ],
    ) -> str:
        return await remove_from_history(history_type, items)

    # Return handlers for type checker visibility
    return (
        fetch_user_ratings_tool,
        add_user_ratings_tool,
        remove_user_ratings_tool,
        fetch_user_watchlist_tool,
        add_user_watchlist_tool,
        remove_user_watchlist_tool,
        fetch_history_tool,
        add_to_history_tool,
        remove_from_history_tool,
    )
