"""Comment endpoints."""

COMMENTS_ENDPOINTS = {
    # Comment endpoints
    "comments_movie": "/movies/:id/comments/:sort",
    "comments_show": "/shows/:id/comments/:sort",
    "comments_season": "/shows/:id/seasons/:season/comments/:sort",
    "comments_episode": "/shows/:id/seasons/:season/episodes/:episode/comments/:sort",
    "comment": "/comments/:id",
    "comment_replies": "/comments/:id/replies/:sort",
}
