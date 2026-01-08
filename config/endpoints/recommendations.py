"""Trakt API endpoints for recommendations."""

RECOMMENDATIONS_ENDPOINTS = {
    "recommendations_movies": "/recommendations/movies",
    "recommendations_shows": "/recommendations/shows",
    "hide_movie_recommendation": "/recommendations/movies/:id",
    "hide_show_recommendation": "/recommendations/shows/:id",
    "unhide_recommendations": "/users/hidden/recommendations/remove",
}
