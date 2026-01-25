"""Playback progress client for Trakt API."""

from typing import Literal

from config.endpoints.progress import PROGRESS_ENDPOINTS
from models.progress.playback import PlaybackProgressResponse
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


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
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to access playback progress")

        # Build the endpoint URL based on type filter
        if playback_type:
            endpoint = PROGRESS_ENDPOINTS["sync_playback_type"].replace(
                ":type", playback_type
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
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to remove playback items")

        # Build the endpoint URL with the playback ID
        endpoint = PROGRESS_ENDPOINTS["sync_playback_remove"].replace(
            ":id", str(playback_id)
        )

        await self._delete_request(endpoint)
