"""Sync ratings functionality for Trakt."""

from typing import Any

from config.endpoints.sync import SYNC_ENDPOINTS
from models.sync.ratings import (
    SyncRatingsSummary,
    TraktSyncRating,
    TraktSyncRatingsRequest,
)
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


class SyncRatingsClient(AuthClient):
    """Client for sync ratings operations."""

    @handle_api_errors
    async def get_sync_ratings(
        self, rating_type: str, rating: int | None = None
    ) -> list[TraktSyncRating]:
        """Get user's personal ratings from sync API.

        Args:
            rating_type: Type of ratings to get (movies, shows, seasons, episodes)
            rating: Optional specific rating to filter by (1-10)

        Returns:
            List of user's ratings for the specified type

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError(
                "You must be authenticated to access your personal ratings"
            )

        # Build the endpoint URL
        if rating is not None:
            endpoint = (
                SYNC_ENDPOINTS["sync_ratings_get"]
                .replace(":type", rating_type)
                .replace(":rating", str(rating))
            )
        else:
            endpoint = SYNC_ENDPOINTS["sync_ratings_get_type"].replace(
                ":type", rating_type
            )

        return await self._make_typed_list_request(
            endpoint, response_type=TraktSyncRating
        )

    @handle_api_errors
    async def add_sync_ratings(
        self, request: TraktSyncRatingsRequest
    ) -> SyncRatingsSummary:
        """Add new ratings for the authenticated user.

        Args:
            request: Rating items to add with ratings data

        Returns:
            Summary of added ratings with counts and any not found items

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to add personal ratings")

        # Convert request to dict, excluding None values
        data: dict[str, Any] = request.model_dump(exclude_none=True)

        return await self._post_typed_request(
            SYNC_ENDPOINTS["sync_ratings_add"], data, response_type=SyncRatingsSummary
        )

    @handle_api_errors
    async def remove_sync_ratings(
        self, request: TraktSyncRatingsRequest
    ) -> SyncRatingsSummary:
        """Remove ratings for the authenticated user.

        Args:
            request: Rating items to remove (should not include rating values, just item identification)

        Returns:
            Summary of removed ratings with counts and any not found items

        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to remove personal ratings")

        # Convert request to dict, excluding None values
        data: dict[str, Any] = request.model_dump(exclude_none=True)

        # Use POST method for sync ratings removal
        return await self._post_typed_request(
            SYNC_ENDPOINTS["sync_ratings_remove"], data, response_type=SyncRatingsSummary
        )
