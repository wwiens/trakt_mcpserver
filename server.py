import asyncio
from typing import Dict, Any
import logging
import json

from mcp.server.fastmcp import Context, FastMCP

from trakt_client import TraktClient
from models import FormatHelper
from config import MCP_RESOURCES, DEFAULT_LIMIT, TOOL_NAMES

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("trakt_mcp")

# Create a named server
mcp = FastMCP("Trakt MCP")

# Show Resources
@mcp.resource(MCP_RESOURCES["shows_trending"])
async def get_trending_shows() -> str:
    """Returns the most watched shows over the last 24 hours from Trakt. Shows with the most watchers are returned first.
    
    Returns:
        Formatted markdown text with trending shows
    """
    client = TraktClient()
    shows = await client.get_trending_shows(limit=DEFAULT_LIMIT)
    return FormatHelper.format_trending_shows(shows)


@mcp.resource(MCP_RESOURCES["shows_popular"])
async def get_popular_shows() -> str:
    """Returns the most popular shows from Trakt. Popularity is calculated using the rating percentage and the number of ratings.
    
    Returns:
        Formatted markdown text with popular shows
    """
    client = TraktClient()
    shows = await client.get_popular_shows(limit=DEFAULT_LIMIT)
    return FormatHelper.format_popular_shows(shows)


@mcp.resource(MCP_RESOURCES["shows_favorited"])
async def get_favorited_shows() -> str:
    """Returns the most favorited shows from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.
    
    Returns:
        Formatted markdown text with most favorited shows
    """
    client = TraktClient()
    shows = await client.get_favorited_shows(limit=DEFAULT_LIMIT)
    
    # Log the first show to see the structure
    if shows and len(shows) > 0:
        logger.info(f"Favorited shows API response structure: {json.dumps(shows[0], indent=2)}")
    
    return FormatHelper.format_favorited_shows(shows)


@mcp.resource(MCP_RESOURCES["shows_played"])
async def get_played_shows() -> str:
    """Returns the most played (a single user can watch multiple episodes multiple times) shows from Traktin the specified time period, defaulting to weekly. All stats are relative to the specific time period.
    
    Returns:
        Formatted markdown text with most played shows
    """
    client = TraktClient()
    shows = await client.get_played_shows(limit=DEFAULT_LIMIT)
    return FormatHelper.format_played_shows(shows)


@mcp.resource(MCP_RESOURCES["shows_watched"])
async def get_watched_shows() -> str:
    """Returns the most watched (unique users) shows from Traktin the specified time period, defaulting to weekly. All stats are relative to the specific time period.
    
    Returns:
        Formatted markdown text with most watched shows
    """
    client = TraktClient()
    shows = await client.get_watched_shows(limit=DEFAULT_LIMIT)
    return FormatHelper.format_watched_shows(shows)

# Movie Resources
@mcp.resource(MCP_RESOURCES["movies_trending"])
async def get_trending_movies() -> str:
    """Returns the most watched movies over the last 24 hours from Trakt. Movies with the most watchers are returned first.
    
    Returns:
        Formatted markdown text with trending movies
    """
    client = TraktClient()
    movies = await client.get_trending_movies(limit=DEFAULT_LIMIT)
    return FormatHelper.format_trending_movies(movies)


@mcp.resource(MCP_RESOURCES["movies_popular"])
async def get_popular_movies() -> str:
    """Returns the most popular movies from Trakt. Popularity is calculated using the rating percentage and the number of ratings.
    
    Returns:
        Formatted markdown text with popular movies
    """
    client = TraktClient()
    movies = await client.get_popular_movies(limit=DEFAULT_LIMIT)
    return FormatHelper.format_popular_movies(movies)


@mcp.resource(MCP_RESOURCES["movies_favorited"])
async def get_favorited_movies() -> str:
    """Returns the most favorited movies from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.
    
    Returns:
        Formatted markdown text with most favorited movies
    """
    client = TraktClient()
    movies = await client.get_favorited_movies(limit=DEFAULT_LIMIT)
    
    # Log the first movie to see the structure
    if movies and len(movies) > 0:
        logger.info(f"Favorited movies API response structure: {json.dumps(movies[0], indent=2)}")
    
    return FormatHelper.format_favorited_movies(movies)


@mcp.resource(MCP_RESOURCES["movies_played"])
async def get_played_movies() -> str:
    """Returns the most played (a single user can watch a single movie multiple times) movies from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.
    
    Returns:
        Formatted markdown text with most played movies
    """
    client = TraktClient()
    movies = await client.get_played_movies(limit=DEFAULT_LIMIT)
    return FormatHelper.format_played_movies(movies)


@mcp.resource(MCP_RESOURCES["movies_watched"])
async def get_watched_movies() -> str:
    """Returns the most watched (unique users) movies from Trakt in the specified time period, defaulting to weekly. All stats are relative to the specific time period.
    
    Returns:
        Formatted markdown text with most watched movies
    """
    client = TraktClient()
    movies = await client.get_watched_movies(limit=DEFAULT_LIMIT)
    return FormatHelper.format_watched_movies(movies)

# Show Tools
@mcp.tool(name=TOOL_NAMES["fetch_trending_shows"])
async def fetch_trending_shows(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch trending shows from Trakt.
    
    Args:
        limit: Maximum number of shows to return
        
    Returns:
        Information about trending shows
    """
    client = TraktClient()
    shows = await client.get_trending_shows(limit=limit)
    return FormatHelper.format_trending_shows(shows)


@mcp.tool(name=TOOL_NAMES["fetch_popular_shows"])
async def fetch_popular_shows(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch popular shows from Trakt.
    
    Args:
        limit: Maximum number of shows to return
        
    Returns:
        Information about popular shows
    """
    client = TraktClient()
    shows = await client.get_popular_shows(limit=limit)
    return FormatHelper.format_popular_shows(shows)


@mcp.tool(name=TOOL_NAMES["fetch_favorited_shows"])
async def fetch_favorited_shows(limit: int = DEFAULT_LIMIT, period: str = "weekly") -> str:
    """Fetch most favorited shows from Trakt.
    
    Args:
        limit: Maximum number of shows to return
        period: Time period for favorite calculation (daily, weekly, monthly, yearly, all)
        
    Returns:
        Information about most favorited shows
    """
    client = TraktClient()
    shows = await client.get_favorited_shows(limit=limit, period=period)
    
    # Log the first show to see the structure
    if shows and len(shows) > 0:
        logger.info(f"Favorited shows API response structure: {json.dumps(shows[0], indent=2)}")
    
    return FormatHelper.format_favorited_shows(shows)


@mcp.tool(name=TOOL_NAMES["fetch_played_shows"])
async def fetch_played_shows(limit: int = DEFAULT_LIMIT, period: str = "weekly") -> str:
    """Fetch most played shows from Trakt.
    
    Args:
        limit: Maximum number of shows to return
        period: Time period for most played (daily, weekly, monthly, yearly, all)
        
    Returns:
        Information about most played shows
    """
    client = TraktClient()
    shows = await client.get_played_shows(limit=limit, period=period)
    return FormatHelper.format_played_shows(shows)


@mcp.tool(name=TOOL_NAMES["fetch_watched_shows"])
async def fetch_watched_shows(limit: int = DEFAULT_LIMIT, period: str = "weekly") -> str:
    """Fetch most watched shows from Trakt.
    
    Args:
        limit: Maximum number of shows to return
        period: Time period for most watched (daily, weekly, monthly, yearly, all)
        
    Returns:
        Information about most watched shows
    """
    client = TraktClient()
    shows = await client.get_watched_shows(limit=limit, period=period)
    return FormatHelper.format_watched_shows(shows)

# Movie Tools
@mcp.tool(name=TOOL_NAMES["fetch_trending_movies"])
async def fetch_trending_movies(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch trending movies from Trakt.
    
    Args:
        limit: Maximum number of movies to return
        
    Returns:
        Information about trending movies
    """
    client = TraktClient()
    movies = await client.get_trending_movies(limit=limit)
    return FormatHelper.format_trending_movies(movies)


@mcp.tool(name=TOOL_NAMES["fetch_popular_movies"])
async def fetch_popular_movies(limit: int = DEFAULT_LIMIT) -> str:
    """Fetch popular movies from Trakt.
    
    Args:
        limit: Maximum number of movies to return
        
    Returns:
        Information about popular movies
    """
    client = TraktClient()
    movies = await client.get_popular_movies(limit=limit)
    return FormatHelper.format_popular_movies(movies)


@mcp.tool(name=TOOL_NAMES["fetch_favorited_movies"])
async def fetch_favorited_movies(limit: int = DEFAULT_LIMIT, period: str = "weekly") -> str:
    """Fetch most favorited movies from Trakt.
    
    Args:
        limit: Maximum number of movies to return
        period: Time period for favorite calculation (daily, weekly, monthly, yearly, all)
        
    Returns:
        Information about most favorited movies
    """
    client = TraktClient()
    movies = await client.get_favorited_movies(limit=limit, period=period)
    
    # Log the first movie to see the structure
    if movies and len(movies) > 0:
        logger.info(f"Favorited movies API response structure: {json.dumps(movies[0], indent=2)}")
    
    return FormatHelper.format_favorited_movies(movies)


@mcp.tool(name=TOOL_NAMES["fetch_played_movies"])
async def fetch_played_movies(limit: int = DEFAULT_LIMIT, period: str = "weekly") -> str:
    """Fetch most played movies from Trakt.
    
    Args:
        limit: Maximum number of movies to return
        period: Time period for most played (daily, weekly, monthly, yearly, all)
        
    Returns:
        Information about most played movies
    """
    client = TraktClient()
    movies = await client.get_played_movies(limit=limit, period=period)
    return FormatHelper.format_played_movies(movies)


@mcp.tool(name=TOOL_NAMES["fetch_watched_movies"])
async def fetch_watched_movies(limit: int = DEFAULT_LIMIT, period: str = "weekly") -> str:
    """Fetch most watched movies from Trakt.
    
    Args:
        limit: Maximum number of movies to return
        period: Time period for most watched (daily, weekly, monthly, yearly, all)
        
    Returns:
        Information about most watched movies
    """
    client = TraktClient()
    movies = await client.get_watched_movies(limit=limit, period=period)
    return FormatHelper.format_watched_movies(movies)


if __name__ == "__main__":
    print("Starting Trakt MCP server...")
    print("Run 'mcp dev server.py' to test with the MCP Inspector")
    print("Run 'mcp install server.py' to install in Claude Desktop")
    mcp.run() 