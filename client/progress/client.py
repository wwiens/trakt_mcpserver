"""Unified progress client that combines all progress functionality."""

from .playback import PlaybackClient
from .show_progress import ShowProgressClient


class ProgressClient(ShowProgressClient, PlaybackClient):
    """Unified client for all progress-related operations.

    Combines functionality from:
    - ShowProgressClient: get_show_progress()
    - PlaybackClient: get_playback_progress(), remove_playback_item()

    Note: History operations (add_to_history, remove_from_history, get_history)
    are now in the SyncClient (client.sync.client).

    Inherits OAuth authentication handling from AuthClient through parent clients.
    All progress operations require user authentication to access personal data.
    """

    pass
