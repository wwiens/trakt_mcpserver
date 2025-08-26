"""Sync tools for the Trakt MCP server."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from client.sync.client import SyncClient
from config.mcp.tools.sync import SYNC_TOOLS
from models.formatters.sync_ratings import SyncRatingsFormatters
from models.sync.ratings import (
    SyncRatingsSummary,
    TraktSyncRating,
    TraktSyncRatingItem,
    TraktSyncRatingsRequest,
)
from server.base import BaseToolErrorMixin
from utils.api.errors import MCPError, handle_api_errors_func

logger = logging.getLogger("trakt_mcp")

# Type alias for tool handlers
ToolHandler = Callable[..., Awaitable[str]]


# Pydantic models for parameter validation
class UserRatingsParams(BaseModel):
    """Parameters for fetching user ratings."""

    rating_type: Literal["movies", "shows", "seasons", "episodes"] = "movies"
    rating: int | None = Field(
        default=None, ge=1, le=10, description="Optional specific rating to filter by"
    )

    @field_validator("rating", mode="before")
    @classmethod
    def _validate_rating(cls, v: object) -> object:
        if v is None or v == "":
            return None
        return v


class UserRatingRequestItem(BaseModel):
    """Single rating item for add/remove operations."""

    rating: int = Field(ge=1, le=10, description="Rating from 1 to 10")
    trakt_id: str | None = Field(default=None, min_length=1, description="Trakt ID")
    imdb_id: str | None = Field(default=None, min_length=1, description="IMDB ID")
    tmdb_id: str | None = Field(default=None, min_length=1, description="TMDB ID")
    title: str | None = Field(default=None, min_length=1, description="Title")
    year: int | None = Field(default=None, gt=1800, description="Release year")

    @field_validator("trakt_id", "imdb_id", "tmdb_id", "title", mode="before")
    @classmethod
    def _strip_strings(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


class UserRatingRequest(BaseModel):
    """Parameters for adding/removing user ratings."""

    rating_type: Literal["movies", "shows", "seasons", "episodes"]
    items: list[UserRatingRequestItem] = Field(
        min_length=1, description="List of items to rate"
    )


@handle_api_errors_func
async def fetch_user_ratings(
    rating_type: Literal["movies", "shows", "seasons", "episodes"] = "movies",
    rating: int | None = None,
) -> str:
    """Fetch authenticated user's personal ratings from Trakt.

    Args:
        rating_type: Type of ratings to fetch (movies, shows, seasons, episodes)
        rating: Optional specific rating to filter by (1-10)

    Returns:
        User's personal ratings formatted as markdown

    Raises:
        AuthenticationRequiredError: If user is not authenticated
    """
    # Validate parameters with Pydantic
    params = UserRatingsParams(rating_type=rating_type, rating=rating)
    rating_type, rating = params.rating_type, params.rating

    try:
        client = SyncClient()
        ratings: list[TraktSyncRating] = await client.get_sync_ratings(
            rating_type, rating
        )

        # Handle transitional case where API returns error strings
        if isinstance(ratings, str):
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"user_{rating_type}_ratings",
                resource_id=f"user_ratings_{rating_type}",
                error_message=ratings,
                operation="fetch_user_ratings",
            )

        return SyncRatingsFormatters.format_user_ratings(ratings, rating_type, rating)
    except MCPError:
        raise


@handle_api_errors_func
async def add_user_ratings(
    rating_type: Literal["movies", "shows", "seasons", "episodes"],
    items: list[dict[str, Any]],
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
    # Validate parameters with Pydantic
    items_list = [UserRatingRequestItem(**item) for item in items]
    params = UserRatingRequest(rating_type=rating_type, items=items_list)
    rating_type, validated_items = params.rating_type, params.items

    try:
        client = SyncClient()

        # Convert to sync request format
        sync_items: list[TraktSyncRatingItem] = []
        for item in validated_items:
            ids: dict[str, Any] = {}

            # Add IDs that are provided
            if item.trakt_id:
                ids["trakt"] = int(item.trakt_id)
            if item.imdb_id:
                ids["imdb"] = item.imdb_id
            if item.tmdb_id:
                ids["tmdb"] = int(item.tmdb_id) if item.tmdb_id.isdigit() else item.tmdb_id

            # Create sync rating item
            sync_item_data: dict[str, Any] = {
                "rating": item.rating,
                "ids": ids,
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
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"add_user_{rating_type}_ratings",
                resource_id=f"add_ratings_{rating_type}",
                error_message=summary,
                operation="add_user_ratings",
            )

        return SyncRatingsFormatters.format_user_ratings_summary(
            summary, "added", rating_type
        )
    except MCPError:
        raise


@handle_api_errors_func
async def remove_user_ratings(
    rating_type: Literal["movies", "shows", "seasons", "episodes"],
    items: list[dict[str, Any]],
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
    # For removal, we don't need ratings, just IDs - but we'll accept the same format
    items_list: list[UserRatingRequestItem] = []
    for item in items:
        # Create a copy without requiring rating for removal
        item_copy = dict(item)
        if "rating" not in item_copy:
            item_copy["rating"] = 1  # Dummy rating for validation, not used in DELETE
        items_list.append(UserRatingRequestItem(**item_copy))

    params = UserRatingRequest(rating_type=rating_type, items=items_list)
    rating_type, validated_items = params.rating_type, params.items

    try:
        client = SyncClient()

        # Convert to sync request format (no ratings needed for removal)
        sync_items: list[TraktSyncRatingItem] = []
        for item in validated_items:
            ids: dict[str, Any] = {}

            # Add IDs that are provided
            if item.trakt_id:
                ids["trakt"] = int(item.trakt_id)
            if item.imdb_id:
                ids["imdb"] = item.imdb_id
            if item.tmdb_id:
                ids["tmdb"] = int(item.tmdb_id) if item.tmdb_id.isdigit() else item.tmdb_id

            # Create sync rating item (no rating for removal)
            sync_item_data: dict[str, Any] = {"ids": ids}

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
            raise BaseToolErrorMixin.handle_api_string_error(
                resource_type=f"remove_user_{rating_type}_ratings",
                resource_id=f"remove_ratings_{rating_type}",
                error_message=summary,
                operation="remove_user_ratings",
            )

        return SyncRatingsFormatters.format_user_ratings_summary(
            summary, "removed", rating_type
        )
    except MCPError:
        raise


def register_sync_tools(mcp: FastMCP) -> tuple[ToolHandler, ToolHandler, ToolHandler]:
    """Register sync rating tools with the MCP server.

    Returns:
        Tuple of tool handlers for type checker visibility
    """

    @mcp.tool(
        name=SYNC_TOOLS["fetch_user_ratings"],
        description="Fetch the authenticated user's personal ratings from Trakt. Requires OAuth authentication.",
    )
    @handle_api_errors_func
    async def fetch_user_ratings_tool(
        rating_type: Literal["movies", "shows", "seasons", "episodes"] = "movies",
        rating: int | None = None,
    ) -> str:
        # Validate parameters with Pydantic
        params = UserRatingsParams(rating_type=rating_type, rating=rating)
        return await fetch_user_ratings(params.rating_type, params.rating)

    @mcp.tool(
        name=SYNC_TOOLS["add_user_ratings"],
        description="Add new ratings for the authenticated user. Requires OAuth authentication.",
    )
    @handle_api_errors_func
    async def add_user_ratings_tool(
        rating_type: Literal["movies", "shows", "seasons", "episodes"],
        items: list[dict[str, Any]],
    ) -> str:
        return await add_user_ratings(rating_type, items)

    @mcp.tool(
        name=SYNC_TOOLS["remove_user_ratings"],
        description="Remove ratings for the authenticated user. Requires OAuth authentication.",
    )
    @handle_api_errors_func
    async def remove_user_ratings_tool(
        rating_type: Literal["movies", "shows", "seasons", "episodes"],
        items: list[dict[str, Any]],
    ) -> str:
        return await remove_user_ratings(rating_type, items)

    # Return handlers for type checker visibility
    return (
        fetch_user_ratings_tool,
        add_user_ratings_tool,
        remove_user_ratings_tool,
    )
