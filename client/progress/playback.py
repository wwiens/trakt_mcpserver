"""Playback progress client for Trakt API."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from config.endpoints.progress import PROGRESS_ENDPOINTS
from models.progress.playback import PlaybackProgressResponse
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


class PlaybackTypeParam(BaseModel):
    """Parameters for playback type filtering."""

    playback_type: Literal["movies", "episodes"] | None = None

    @field_validator("playback_type", mode="before")
    @classmethod
    def _strip_type(cls, v: object) -> object:
        """Strip whitespace if string."""
        return v.strip() if isinstance(v, str) else v


class PlaybackIdParam(BaseModel):
    """Parameters for playback item removal."""

    playback_id: int = Field(
        ..., gt=0, description="Playback item ID (must be positive)"
    )


class PlaybackClient(AuthClient):
    """Client for playback progress operations."""

    @handle_api_errors
    async def get_playback_progress(
        self,
        playback_type: Literal["movies", "episodes"] | None = None,
    ) -> list[PlaybackProgressResponse]:
        """Get paused playback progress items.

        Args:
            playback_type: Filter by type ('movies', 'episodes'), or None for all

        Returns:
            List of playback progress items with progress percentage and metadata

        Raises:
            ValueError: If not authenticated
            ValidationError: If playback_type is invalid
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to access playback progress")

        # Validate input
        params = PlaybackTypeParam(playback_type=playback_type)
        validated_type = params.playback_type

        # Build the endpoint URL based on type filter
        if validated_type:
            endpoint = PROGRESS_ENDPOINTS["sync_playback_type"].replace(
                ":type", validated_type
            )
        else:
            endpoint = PROGRESS_ENDPOINTS["sync_playback"]

        return await self._make_typed_list_request(
            endpoint, response_type=PlaybackProgressResponse
        )

    @handle_api_errors
    async def remove_playback_item(self, playback_id: int) -> None:
        """Remove a playback progress item.

        Args:
            playback_id: ID of the playback item to remove

        Raises:
            ValueError: If not authenticated
            ValidationError: If playback_id is not a positive integer
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to remove playback items")

        # Validate input (ensures playback_id > 0)
        params = PlaybackIdParam(playback_id=playback_id)

        # Build the endpoint URL with the playback ID
        endpoint = PROGRESS_ENDPOINTS["sync_playback_remove"].replace(
            ":id", str(params.playback_id)
        )

        await self._delete_request(endpoint)
