"""Sync endpoints for the Trakt MCP server."""

SYNC_ENDPOINTS = {
    # Rating endpoints
    "sync_ratings_get": "/sync/ratings/:type/:rating",
    "sync_ratings_get_type": "/sync/ratings/:type",
    "sync_ratings_add": "/sync/ratings",
    "sync_ratings_remove": "/sync/ratings/remove",
}
