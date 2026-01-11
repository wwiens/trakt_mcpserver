"""Show-specific MCP resource URI definitions."""

from typing import Final

# Show MCP Resource URIs
SHOW_RESOURCES: Final[dict[str, str]] = {
    "shows_trending": "trakt://shows/trending",
    "shows_popular": "trakt://shows/popular",
    "shows_favorited": "trakt://shows/favorited",
    "shows_played": "trakt://shows/played",
    "shows_watched": "trakt://shows/watched",
}
