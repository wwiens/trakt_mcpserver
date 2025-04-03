"""Configuration for the Trakt MCP server."""

# Trakt API endpoints
TRAKT_ENDPOINTS = {
    "shows_trending": "/shows/trending",
    "shows_popular": "/shows/popular",
    "shows_favorited": "/shows/favorited",
    "shows_played": "/shows/played",
    "shows_watched": "/shows/watched",
    
    # Movie endpoints
    "movies_trending": "/movies/trending",
    "movies_popular": "/movies/popular",
    "movies_favorited": "/movies/favorited",
    "movies_played": "/movies/played",
    "movies_watched": "/movies/watched",
    
    # User authentication endpoints
    "device_code": "/oauth/device/code",
    "device_token": "/oauth/device/token",
    
    # User-specific endpoints
    "user_watched_shows": "/sync/watched/shows",
}

# MCP resource URIs
MCP_RESOURCES = {
    "shows_trending": "trakt://shows/trending",
    "shows_popular": "trakt://shows/popular",
    "shows_favorited": "trakt://shows/favorited",
    "shows_played": "trakt://shows/played",
    "shows_watched": "trakt://shows/watched",
    
    # Movie resources
    "movies_trending": "trakt://movies/trending",
    "movies_popular": "trakt://movies/popular",
    "movies_favorited": "trakt://movies/favorited",
    "movies_played": "trakt://movies/played",
    "movies_watched": "trakt://movies/watched",
    
    # User resources
    "user_auth_status": "trakt://user/auth/status",
    "user_watched_shows": "trakt://user/watched/shows",
}

# Default limits for API requests
DEFAULT_LIMIT = 10

# Authentication settings
AUTH_POLL_INTERVAL = 5  # seconds
AUTH_EXPIRATION = 600  # seconds (10 minutes)
AUTH_VERIFICATION_URL = "https://trakt.tv/activate"

# Tool names
TOOL_NAMES = {
    "fetch_trending_shows": "fetch_trending_shows",
    "fetch_popular_shows": "fetch_popular_shows",
    "fetch_favorited_shows": "fetch_favorited_shows",
    "fetch_played_shows": "fetch_played_shows",
    "fetch_watched_shows": "fetch_watched_shows",
    
    # Movie tools
    "fetch_trending_movies": "fetch_trending_movies",
    "fetch_popular_movies": "fetch_popular_movies",
    "fetch_favorited_movies": "fetch_favorited_movies",
    "fetch_played_movies": "fetch_played_movies",
    "fetch_watched_movies": "fetch_watched_movies",
    
    # User authentication tools
    "start_device_auth": "start_device_auth",
    "check_auth_status": "check_auth_status",
    "clear_auth": "clear_auth",
    
    # User-specific tools
    "fetch_user_watched_shows": "fetch_user_watched_shows",
} 