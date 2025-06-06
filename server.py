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


@mcp.resource(MCP_RESOURCES["user_watched_movies"])
async def get_user_watched_movies() -> str:
    """Returns movies that the authenticated user has watched.
    Requires authentication with Trakt.

    Returns:
        Formatted markdown text with user's watched movies
    """
    client = TraktClient()

    if not client.is_authenticated():
        return "# Authentication Required\n\nYou need to authenticate with Trakt to view your watched movies.\nUse the `start_device_auth` tool to begin authentication."

    movies = await client.get_user_watched_movies()
    return FormatHelper.format_user_watched_movies(movies)


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
    instructions = FormatHelper.format_device_auth_instructions(
        device_code_response.user_code,
        AUTH_VERIFICATION_URL,
        device_code_response.expires_in
    )

    return f"""{instructions}

I won't automatically check your authentication status until you tell me you've completed the authorization. Once you've finished the authorization process on the Trakt website, simply tell me "I've completed the authorization" and I'll verify it for you."""


@mcp.tool(name=TOOL_NAMES["check_auth_status"])
async def check_auth_status() -> str:
    """Check the status of an ongoing device authentication flow.

    Returns:
        Status of the authentication process
    """
    client = TraktClient()

    # Check if already authenticated
    if client.is_authenticated():
        return """# Authentication Successful!

You are now authenticated with Trakt. You can access your personal data using tools like `fetch_user_watched_shows` and `fetch_user_watched_movies`.

If you want to log out at any point, you can use the `clear_auth` tool."""

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
        return """# Authentication Successful!

You have successfully authorized the Trakt MCP application. You can now access your personal Trakt data using tools like `fetch_user_watched_shows` and `fetch_user_watched_movies`.

If you want to log out at any point, you can use the `clear_auth` tool."""
    else:
        # Still waiting for user to authorize
        return """# Authorization Pending

I don't see that you've completed the authorization yet. Please make sure to:

1. Visit the Trakt activation page
2. Enter your code
3. Approve the authorization request

If you've already done this and are still seeing this message, please wait a few seconds and try again by telling me "Please check my authorization status"."""


@mcp.tool(name=TOOL_NAMES["clear_auth"])
async def clear_auth() -> str:
    """Clear the authentication token, effectively logging the user out of Trakt.

    Returns:
        Status message about the logout
    """
    client = TraktClient()

    # Clear any active authentication flow
    global active_auth_flow
    active_auth_flow = {}

    # Try to clear the token
    if client.clear_auth_token():
        return "You have been successfully logged out of Trakt. Your authentication token has been cleared."
    else:
        return "You were not authenticated with Trakt."


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
        return f"""Authentication required to access your watched shows.

{auth_instructions}

After you've completed the authorization process on the Trakt website, please tell me "I've completed the authorization" so I can check if it was successful and retrieve your watched shows."""

    shows = await client.get_user_watched_shows()

    # Apply limit if requested
    if limit > 0 and len(shows) > limit:
        shows = shows[:limit]

    return FormatHelper.format_user_watched_shows(shows)


@mcp.tool(name=TOOL_NAMES["fetch_user_watched_movies"])
async def fetch_user_watched_movies(limit: int = 0) -> str:
    """Fetch movies watched by the authenticated user from Trakt.

    Args:
        limit: Maximum number of movies to return (0 for all)

    Returns:
        Information about user's watched movies
    """
    client = TraktClient()

    if not client.is_authenticated():
        # Start the auth flow automatically
        auth_instructions = await start_device_auth()
        return f"""Authentication required to access your watched movies.

{auth_instructions}

After you've completed the authorization process on the Trakt website, please tell me "I've completed the authorization" so I can check if it was successful and retrieve your watched movies."""

    movies = await client.get_user_watched_movies()

    # Apply limit if requested
    if limit > 0 and len(movies) > limit:
        movies = movies[:limit]

    return FormatHelper.format_user_watched_movies(movies)


@mcp.tool(name=TOOL_NAMES["search_shows"])
async def search_shows(query: str, limit: int = DEFAULT_LIMIT) -> str:
    """Search for shows on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted search results
    """
    client = TraktClient()

    # Perform the search
    results = await client.search_shows(query, limit)

    # Format and return the results
    return FormatHelper.format_show_search_results(results)


@mcp.tool(name=TOOL_NAMES["checkin_to_show"])
async def checkin_to_show(season: int, episode: int, show_id: str = None, show_title: str = None,
                         show_year: int = None, message: str = "", share_twitter: bool = False,
                         share_mastodon: bool = False, share_tumblr: bool = False) -> str:
    """Check in to a show episode that the user is currently watching.

    This will mark the episode as watched on Trakt and can optionally share to connected social media.
    First use the search_shows tool to find the correct show_id before checking in, or provide the show title.

    Args:
        season: Season number
        episode: Episode number
        show_id: Trakt ID for the show (use search_shows to find this, optional if show_title is provided)
        show_title: Title of the show (optional if show_id is provided)
        show_year: Year the show was released (optional, can help with ambiguous titles)
        message: Optional message to include with the checkin
        share_twitter: Whether to share this checkin on Twitter
        share_mastodon: Whether to share this checkin on Mastodon
        share_tumblr: Whether to share this checkin on Tumblr

    Returns:
        Confirmation of the checkin
    """
    client = TraktClient()

    if not client.is_authenticated():
        # Start the auth flow automatically
        auth_instructions = await start_device_auth()
        return f"""Authentication required to check in to a show.

{auth_instructions}

After you've completed the authorization process on the Trakt website, please tell me "I've completed the authorization" so I can check if it was successful and check you in to the show."""

    # Validate that either show_id or show_title is provided
    if not show_id and not show_title:
        return "Error: You must provide either a show_id or a show_title. Use the search_shows tool to find the correct show ID."

    try:
        # Attempt to check in to the show
        response = await client.checkin_to_show(
            episode_season=season,
            episode_number=episode,
            show_id=show_id,
            show_title=show_title,
            show_year=show_year,
            message=message,
            share_twitter=share_twitter,
            share_mastodon=share_mastodon,
            share_tumblr=share_tumblr
        )

        # Format the response
        return FormatHelper.format_checkin_response(response)
    except ValueError as e:
        # Handle authentication errors
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle other errors
        logger.error(f"Error checking in to show: {e}")
        return f"""An error occurred while checking in to the show: {str(e)}

Make sure you provided either:
1. A valid show ID (use search_shows to find it)
   Example: `search_shows(query="Breaking Bad")`

OR

2. A show title (and optionally the year)
   Example: `checkin_to_show(show_title="Breaking Bad", show_year=2008, season=1, episode=1)`"""


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


@mcp.tool(name=TOOL_NAMES["fetch_movie_comments"])
async def fetch_movie_comments(movie_id: str, limit: int = DEFAULT_LIMIT, show_spoilers: bool = False, sort: str = "newest") -> str:
    """Fetch comments for a movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about movie comments
    """
    client = TraktClient()

    try:
        movie = await client.get_movie(movie_id)
        if isinstance(movie, str):
            return f"Error fetching comments for Movie ID: {movie_id}: {movie}"
        title = f"Movie: {movie.get('title', 'Unknown')}"
        
        comments = await client.get_movie_comments(movie_id, limit=limit, sort=sort)
        if isinstance(comments, str):
            return f"Error fetching comments for {title}: {comments}"
        return FormatHelper.format_comments(comments, title, show_spoilers=show_spoilers)
    except Exception as e:
        return f"Error fetching comments for Movie ID: {movie_id}: {str(e)}"

@mcp.tool(name=TOOL_NAMES["fetch_show_comments"])
async def fetch_show_comments(show_id: str, limit: int = DEFAULT_LIMIT, show_spoilers: bool = False, sort: str = "newest") -> str:
    """Fetch comments for a show from Trakt.

    Args:
        show_id: Trakt ID of the show
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about show comments
    """
    client = TraktClient()

    try:
        show = await client.get_show(show_id)
        if isinstance(show, str):
            return f"Error fetching comments for Show ID: {show_id}: {show}"
        title = f"Show: {show.get('title', 'Unknown')}"
        
        comments = await client.get_show_comments(show_id, limit=limit, sort=sort)
        if isinstance(comments, str):
            return f"Error fetching comments for {title}: {comments}"
        return FormatHelper.format_comments(comments, title, show_spoilers=show_spoilers)
    except Exception as e:
        return f"Error fetching comments for Show ID: {show_id}: {str(e)}"

@mcp.tool(name=TOOL_NAMES["fetch_season_comments"])
async def fetch_season_comments(show_id: str, season: int, limit: int = DEFAULT_LIMIT, show_spoilers: bool = False, sort: str = "newest") -> str:
    """Fetch comments for a season from Trakt.

    Args:
        show_id: Trakt ID of the show
        season: Season number
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about season comments
    """
    client = TraktClient()

    try:
        show = await client.get_show(show_id)
        if isinstance(show, str):
            return f"Error fetching comments for Show ID: {show_id} - Season {season}: {show}"
        title = f"Show: {show.get('title', 'Unknown')} - Season {season}"
        
        comments = await client.get_season_comments(show_id, season, limit=limit, sort=sort)
        if isinstance(comments, str):
            return f"Error fetching comments for {title}: {comments}"
        return FormatHelper.format_comments(comments, title, show_spoilers=show_spoilers)
    except Exception as e:
        return f"Error fetching comments for Show ID: {show_id} - Season {season}: {str(e)}"

@mcp.tool(name=TOOL_NAMES["fetch_episode_comments"])
async def fetch_episode_comments(show_id: str, season: int, episode: int, limit: int = DEFAULT_LIMIT, show_spoilers: bool = False, sort: str = "newest") -> str:
    """Fetch comments for an episode from Trakt.

    Args:
        show_id: Trakt ID of the show
        season: Season number
        episode: Episode number
        limit: Maximum number of comments to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about episode comments
    """
    client = TraktClient()

    try:
        show = await client.get_show(show_id)
        if isinstance(show, str):
            return f"Error fetching comments for Show ID: {show_id} - S{season:02d}E{episode:02d}: {show}"
        title = f"Show: {show.get('title', 'Unknown')} - S{season:02d}E{episode:02d}"
        
        comments = await client.get_episode_comments(show_id, season, episode, limit=limit, sort=sort)
        if isinstance(comments, str):
            return f"Error fetching comments for {title}: {comments}"
        return FormatHelper.format_comments(comments, title, show_spoilers=show_spoilers)
    except Exception as e:
        return f"Error fetching comments for Show ID: {show_id} - S{season:02d}E{episode:02d}: {str(e)}"

@mcp.tool(name=TOOL_NAMES["fetch_comment"])
async def fetch_comment(comment_id: str, show_spoilers: bool = False) -> str:
    """Fetch a specific comment from Trakt.

    Args:
        comment_id: Trakt ID of the comment
        show_spoilers: Whether to show spoilers by default

    Returns:
        Information about the comment
    """
    client = TraktClient()
    try:
        comment = await client.get_comment(comment_id)
        if isinstance(comment, str):
            return f"Error fetching comment {comment_id}: {comment}"
        return FormatHelper.format_comment(comment, show_spoilers=show_spoilers)
    except Exception as e:
        return f"Error fetching comment {comment_id}: {str(e)}"

@mcp.tool(name=TOOL_NAMES["fetch_comment_replies"])
async def fetch_comment_replies(comment_id: str, limit: int = DEFAULT_LIMIT, show_spoilers: bool = False, sort: str = "newest") -> str:
    """Fetch replies for a comment from Trakt.

    Args:
        comment_id: Trakt ID of the comment
        limit: Maximum number of replies to return
        show_spoilers: Whether to show spoilers by default
        sort: How to sort replies (newest, oldest, likes, replies, highest, lowest, plays, watched)

    Returns:
        Information about the comment and its replies
    """
    client = TraktClient()
    try:
        comment = await client.get_comment(comment_id)
        if isinstance(comment, str):
            return f"Error fetching comment replies for {comment_id}: {comment}"
        replies = await client.get_comment_replies(comment_id, limit=limit, sort=sort)
        if isinstance(replies, str):
            return f"Error fetching comment replies for {comment_id}: {replies}"
        return FormatHelper.format_comment(comment, with_replies=True, replies=replies, show_spoilers=show_spoilers)
    except Exception as e:
        return f"Error fetching comment replies for {comment_id}: {str(e)}"


@mcp.tool(name=TOOL_NAMES["search_movies"])
async def search_movies(query: str, limit: int = DEFAULT_LIMIT) -> str:
    """Search for movies on Trakt by title.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Formatted search results
    """
    client = TraktClient()
    results = await client.search_movies(query, limit)
    return FormatHelper.format_movie_search_results(results)


@mcp.tool(name=TOOL_NAMES["fetch_show_ratings"])
async def fetch_show_ratings(show_id: str) -> str:
    """Fetch ratings for a show from Trakt.

    Args:
        show_id: Trakt ID of the show

    Returns:
        Information about show ratings including average and distribution
    """
    client = TraktClient()

    try:
        show = await client.get_show(show_id)
        
        # Check if the API returned an error string
        if isinstance(show, str):
            return f"Error fetching ratings for show ID {show_id}: {show}"
            
        show_title = show.get("title", f"Show ID: {show_id}")

        ratings = await client.get_show_ratings(show_id)
        
        # Check if the API returned an error string
        if isinstance(ratings, str):
            return f"Error fetching ratings for {show_title}: {ratings}"

        return FormatHelper.format_show_ratings(ratings, show_title)
    except Exception as e:
        logger.error(f"Error fetching show ratings: {e}")
        return f"Error fetching ratings for show ID {show_id}: {str(e)}"


@mcp.tool(name=TOOL_NAMES["fetch_movie_ratings"])
async def fetch_movie_ratings(movie_id: str) -> str:
    """Fetch ratings for a movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie

    Returns:
        Information about movie ratings including average and distribution
    """
    client = TraktClient()

    try:
        movie = await client.get_movie(movie_id)
        
        # Check if the API returned an error string
        if isinstance(movie, str):
            return f"Error fetching ratings for movie ID {movie_id}: {movie}"
            
        movie_title = movie.get("title", f"Movie ID: {movie_id}")

        ratings = await client.get_movie_ratings(movie_id)
        
        # Check if the API returned an error string
        if isinstance(ratings, str):
            return f"Error fetching ratings for {movie_title}: {ratings}"

        return FormatHelper.format_movie_ratings(ratings, movie_title)
    except Exception as e:
        logger.error(f"Error fetching movie ratings: {e}")
        return f"Error fetching ratings for movie ID {movie_id}: {str(e)}"


@mcp.resource(MCP_RESOURCES["show_ratings"])
async def get_show_ratings(show_id: str) -> str:
    """Returns ratings for a specific show from Trakt.

    Args:
        show_id: Trakt ID of the show

    Returns:
        Formatted markdown text with show ratings
    """
    client = TraktClient()

    try:
        show = await client.get_show(show_id)
        
        # Check if the API returned an error string
        if isinstance(show, str):
            return f"Error fetching ratings for show ID {show_id}: {show}"
            
        show_title = show.get("title", f"Show ID: {show_id}")

        ratings = await client.get_show_ratings(show_id)
        
        # Check if the API returned an error string
        if isinstance(ratings, str):
            return f"Error fetching ratings for {show_title}: {ratings}"

        return FormatHelper.format_show_ratings(ratings, show_title)
    except Exception as e:
        logger.error(f"Error fetching show ratings: {e}")
        return f"Error fetching ratings for show ID {show_id}: {str(e)}"


@mcp.resource(MCP_RESOURCES["movie_ratings"])
async def get_movie_ratings(movie_id: str) -> str:
    """Returns ratings for a specific movie from Trakt.

    Args:
        movie_id: Trakt ID of the movie

    Returns:
        Formatted markdown text with movie ratings
    """
    client = TraktClient()

    try:
        movie = await client.get_movie(movie_id)
        
        # Check if the API returned an error string
        if isinstance(movie, str):
            return f"Error fetching ratings for movie ID {movie_id}: {movie}"
            
        movie_title = movie.get("title", f"Movie ID: {movie_id}")

        ratings = await client.get_movie_ratings(movie_id)
        
        # Check if the API returned an error string
        if isinstance(ratings, str):
            return f"Error fetching ratings for {movie_title}: {ratings}"

        return FormatHelper.format_movie_ratings(ratings, movie_title)
    except Exception as e:
        logger.error(f"Error fetching movie ratings: {e}")
        return f"Error fetching ratings for movie ID {movie_id}: {str(e)}"


if __name__ == "__main__":
    print("Starting Trakt MCP server...")
    print("Run 'mcp dev server.py' to test with the MCP Inspector")
    print("Run 'mcp install server.py' to install in Claude Desktop")
    mcp.run()
