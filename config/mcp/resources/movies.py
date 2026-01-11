"""Movie-specific MCP resource URI definitions."""

from typing import Final

# Movie MCP Resource URIs
MOVIE_RESOURCES: Final[dict[str, str]] = {
    "movies_trending": "trakt://movies/trending",
    "movies_popular": "trakt://movies/popular",
    "movies_favorited": "trakt://movies/favorited",
    "movies_played": "trakt://movies/played",
    "movies_watched": "trakt://movies/watched",
}
