"""Sync endpoints for the Trakt MCP server."""

from collections.abc import Mapping
from typing import Final

# Sync API endpoints (placeholders use colon syntax and are expanded by client helpers)
SYNC_ENDPOINTS: Final[Mapping[str, str]] = {
    # Rating endpoints
    "sync_ratings_get": "/sync/ratings/:type/:rating",
    "sync_ratings_get_type": "/sync/ratings/:type",
    "sync_ratings_add": "/sync/ratings",
    "sync_ratings_remove": "/sync/ratings/remove",
}
