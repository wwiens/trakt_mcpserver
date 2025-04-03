import asyncio
from typing import Dict, Any, Optional
import logging
import json
import time

from mcp.server.fastmcp import Context, FastMCP

from trakt_client import TraktClient
from models import FormatHelper, TraktDeviceCode
from config import MCP_RESOURCES, DEFAULT_LIMIT, TOOL_NAMES, AUTH_POLL_INTERVAL, AUTH_VERIFICATION_URL

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("trakt_mcp")

# Create a named server
mcp = FastMCP("Trakt MCP")

# Authentication storage for active device code flows
active_auth_flow = {}

# Authentication Resources
@mcp.resource(MCP_RESOURCES["user_auth_status"])
async def get_auth_status() -> str:
    """Returns the current authentication status with Trakt.
    
    Returns:
        Formatted markdown text with authentication status
    """
    client = TraktClient()
    is_authenticated = client.is_authenticated()
    expires_at = client.get_token_expiry() if is_authenticated else None
    return FormatHelper.format_auth_status(is_authenticated, expires_at)


# User Resources
@mcp.resource(MCP_RESOURCES["user_watched_shows"])
async def get_user_watched_shows() -> str:
    """Returns shows that the authenticated user has watched.
    Requires authentication with Trakt.
    
    Returns:
        Formatted markdown text with user's watched shows
    """
    client = TraktClient()
    
    if not client.is_authenticated():
        return "# Authentication Required\n\nYou need to authenticate with Trakt to view your watched shows.\nUse the `start_device_auth` tool to begin authentication."
    
    shows = await client.get_user_watched_shows()
    return FormatHelper.format_user_watched_shows(shows)


# Authentication Tools
@mcp.tool(name=TOOL_NAMES["start_device_auth"])
async def start_device_auth() -> str:
    """Start the device authentication flow with Trakt.
    
    Returns:
        Authentication instructions for the user
    """
    client = TraktClient()
    
    # Check if already authenticated
    if client.is_authenticated():
        return "You are already authenticated with Trakt."
    
    # Get device code
    device_code_response = await client.get_device_code()
    
    # Store active auth flow
    global active_auth_flow
    active_auth_flow = {
        "device_code": device_code_response.device_code,
        "expires_at": int(time.time()) + device_code_response.expires_in,
        "interval": device_code_response.interval,
        "last_poll": 0
    }
    
    logger.info(f"Started device auth flow: {active_auth_flow}")
    
    # Return instructions for the user
    return FormatHelper.format_device_auth_instructions(
        device_code_response.user_code,
        AUTH_VERIFICATION_URL,
        device_code_response.expires_in
    )


@mcp.tool(name=TOOL_NAMES["check_auth_status"])
async def check_auth_status() -> str:
    """Check the status of an ongoing device authentication flow.
    
    Returns:
        Status of the authentication process
    """
    client = TraktClient()
    
    # Check if already authenticated
    if client.is_authenticated():
        return "You are authenticated with Trakt."
    
    # Check if there's an active flow
    global active_auth_flow
    if not active_auth_flow or "device_code" not in active_auth_flow:
        return "No active authentication flow. Use the `start_device_auth` tool to begin authentication."
    
    # Check if flow is expired
    current_time = int(time.time())
    if current_time > active_auth_flow["expires_at"]:
        active_auth_flow = {}
        return "Authentication flow expired. Please start a new one with the `start_device_auth` tool."
    
    # Check if it's too early to poll again
    if current_time - active_auth_flow["last_poll"] < active_auth_flow["interval"]:
        seconds_to_wait = active_auth_flow["interval"] - (current_time - active_auth_flow["last_poll"])
        return f"Please wait {seconds_to_wait} seconds before checking again."
    
    # Update last poll time
    active_auth_flow["last_poll"] = current_time
    
    # Try to get token
    token = await client.get_device_token(active_auth_flow["device_code"])
    if token:
        # Authentication successful
        active_auth_flow = {}
        return "Authentication successful! You can now access your personal Trakt data."
    else:
        # Still waiting for user to authorize
        return "Waiting for authorization... Please complete the steps provided earlier."


@mcp.tool(name=TOOL_NAMES["fetch_user_watched_shows"])
async def fetch_user_watched_shows(limit: int = 0) -> str:
    """Fetch shows watched by the authenticated user from Trakt.
    
    Args:
        limit: Maximum number of shows to return (0 for all)
        
    Returns:
        Information about user's watched shows
    """
    client = TraktClient()
    
    if not client.is_authenticated():
        # Start the auth flow automatically
        auth_instructions = await start_device_auth()
        return f"Authentication required to access your watched shows.\n\n{auth_instructions}"
    
    shows = await client.get_user_watched_shows()
    
    # Apply limit if requested
    if limit > 0 and len(shows) > limit:
        shows = shows[:limit]
    
    return FormatHelper.format_user_watched_shows(shows)

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