"""Unified sync client that combines all sync functionality."""

from .ratings_client import SyncRatingsClient


class SyncClient(SyncRatingsClient):
    """Unified client for all sync-related operations.

    Combines functionality from:
    - SyncRatingsClient: get_sync_ratings(), add_sync_ratings(), remove_sync_ratings()

    Note: Inherits OAuth authentication handling from AuthClient through SyncRatingsClient.
    All sync operations require user authentication to access personal data.
    """

    pass
