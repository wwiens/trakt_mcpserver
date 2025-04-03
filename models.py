from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import json


class TraktShow(BaseModel):
    """Represents a Trakt show."""
    title: str
    year: Optional[int] = None
    ids: Dict[str, str] = Field(description="Various IDs for the show (trakt, slug, tvdb, imdb, tmdb)")
    overview: Optional[str] = None
    

class TraktMovie(BaseModel):
    """Represents a Trakt movie."""
    title: str
    year: Optional[int] = None
    ids: Dict[str, str] = Field(description="Various IDs for the movie (trakt, slug, tmdb, imdb)")
    overview: Optional[str] = None


class TraktTrendingShow(BaseModel):
    """Represents a trending show from Trakt API."""
    watchers: int = Field(description="Number of people watching this show")
    show: TraktShow


class TraktTrendingMovie(BaseModel):
    """Represents a trending movie from Trakt API."""
    watchers: int = Field(description="Number of people watching this movie")
    movie: TraktMovie


class TraktPopularShow(BaseModel):
    """Represents a popular show from Trakt API."""
    show: TraktShow = Field(description="The show information")
    
    @classmethod
    def from_api_response(cls, api_data: Dict) -> "TraktPopularShow":
        """Create a TraktPopularShow instance from raw API data."""
        return cls(show=TraktShow(**api_data))


class TraktPopularMovie(BaseModel):
    """Represents a popular movie from Trakt API."""
    movie: TraktMovie = Field(description="The movie information")
    
    @classmethod
    def from_api_response(cls, api_data: Dict) -> "TraktPopularMovie":
        """Create a TraktPopularMovie instance from raw API data."""
        return cls(movie=TraktMovie(**api_data))


class TraktDeviceCode(BaseModel):
    """Response from Trakt for device code authentication."""
    device_code: str
    user_code: str
    verification_url: str
    expires_in: int
    interval: int


class TraktAuthToken(BaseModel):
    """Authentication token response from Trakt."""
    access_token: str
    refresh_token: str
    expires_in: int
    created_at: int
    scope: str = "public"
    token_type: str = "bearer"


class TraktEpisode(BaseModel):
    """Represents a Trakt episode."""
    season: int
    number: int
    title: Optional[str] = None
    ids: Optional[Dict[str, str]] = None
    last_watched_at: Optional[str] = None


class TraktUserShow(BaseModel):
    """Represents a show watched by a user."""
    show: TraktShow
    last_watched_at: str
    last_updated_at: str
    seasons: Optional[List[Dict]] = None
    plays: int


class FormatHelper:
    """Helper class for formatting Trakt data for MCP responses."""
    
    @staticmethod
    def format_trending_shows(shows: List[Dict]) -> str:
        """Format trending shows data for MCP resource."""
        result = "# Trending Shows on Trakt\n\n"
        
        for item in shows:
            show = item.get("show", {})
            watchers = item.get("watchers", 0)
            
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - {watchers} watchers\n"
            
            if overview := show.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_popular_shows(shows: List[Dict]) -> str:
        """Format popular shows data for MCP resource."""
        result = "# Popular Shows on Trakt\n\n"
        
        for show in shows:
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}**\n"
            
            if overview := show.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_favorited_shows(shows: List[Dict]) -> str:
        """Format favorited shows data for MCP resource."""
        result = "# Most Favorited Shows on Trakt\n\n"
        
        for item in shows:
            show = item.get("show", {})
            # The correct field is user_count in the API response
            user_count = item.get("user_count", 0)
            
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - Favorited by {user_count} users\n"
            
            if overview := show.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_played_shows(shows: List[Dict]) -> str:
        """Format played shows data for MCP resource."""
        result = "# Most Played Shows on Trakt\n\n"
        
        for item in shows:
            show = item.get("show", {})
            watcher_count = item.get("watcher_count", 0)
            play_count = item.get("play_count", 0)
            
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - {watcher_count} watchers, {play_count} plays\n"
            
            if overview := show.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_watched_shows(shows: List[Dict]) -> str:
        """Format watched shows data for MCP resource."""
        result = "# Most Watched Shows on Trakt\n\n"
        
        for item in shows:
            show = item.get("show", {})
            watcher_count = item.get("watcher_count", 0)
            
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - Watched by {watcher_count} users\n"
            
            if overview := show.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
        
    # Movie formatting methods
    @staticmethod
    def format_trending_movies(movies: List[Dict]) -> str:
        """Format trending movies data for MCP resource."""
        result = "# Trending Movies on Trakt\n\n"
        
        for item in movies:
            movie = item.get("movie", {})
            watchers = item.get("watchers", 0)
            
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - {watchers} watchers\n"
            
            if overview := movie.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_popular_movies(movies: List[Dict]) -> str:
        """Format popular movies data for MCP resource."""
        result = "# Popular Movies on Trakt\n\n"
        
        for movie in movies:
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}**\n"
            
            if overview := movie.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_favorited_movies(movies: List[Dict]) -> str:
        """Format favorited movies data for MCP resource."""
        result = "# Most Favorited Movies on Trakt\n\n"
        
        for item in movies:
            movie = item.get("movie", {})
            # The correct field is user_count in the API response
            user_count = item.get("user_count", 0)
            
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - Favorited by {user_count} users\n"
            
            if overview := movie.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_played_movies(movies: List[Dict]) -> str:
        """Format played movies data for MCP resource."""
        result = "# Most Played Movies on Trakt\n\n"
        
        for item in movies:
            movie = item.get("movie", {})
            watcher_count = item.get("watcher_count", 0)
            play_count = item.get("play_count", 0)
            
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - {watcher_count} watchers, {play_count} plays\n"
            
            if overview := movie.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_watched_movies(movies: List[Dict]) -> str:
        """Format watched movies data for MCP resource."""
        result = "# Most Watched Movies on Trakt\n\n"
        
        for item in movies:
            movie = item.get("movie", {})
            watcher_count = item.get("watcher_count", 0)
            
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - Watched by {watcher_count} users\n"
            
            if overview := movie.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
    
    @staticmethod
    def format_auth_status(is_authenticated: bool, expires_at: Optional[int] = None) -> str:
        """Format authentication status for MCP resource."""
        if is_authenticated:
            return f"# Authentication Status\n\nYou are authenticated with Trakt.\nToken expires at: {expires_at}"
        else:
            return "# Authentication Status\n\nYou are not authenticated with Trakt.\nUse the `start_device_auth` tool to authenticate."
    
    @staticmethod
    def format_device_auth_instructions(user_code: str, verification_url: str, expires_in: int) -> str:
        """Format device authentication instructions."""
        minutes = int(expires_in / 60)
        return f"""# Trakt Authentication Required

To access your personal Trakt data, you need to authenticate with Trakt.

1. Visit: **{verification_url}**
2. Enter code: **{user_code}**
3. Complete the authorization process on the Trakt website
4. **Important**: After authorizing on the Trakt website, please tell me "I've completed the authorization" so I can check your authentication status.

This code will expire in {minutes} minutes. I'll wait for your confirmation that you've completed the authorization step before checking.
"""
    
    @staticmethod
    def format_user_watched_shows(shows: List[Dict]) -> str:
        """Format user watched shows data for MCP resource."""
        result = "# Your Watched Shows on Trakt\n\n"
        
        if not shows:
            return result + "You haven't watched any shows yet, or you need to authenticate first."
        
        for item in shows:
            show = item.get("show", {})
            last_watched = item.get("last_watched_at", "Unknown")
            plays = item.get("plays", 0)
            
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - Watched: {last_watched}, Plays: {plays}\n"
            
            if overview := show.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
        
    @staticmethod
    def format_user_watched_movies(movies: List[Dict]) -> str:
        """Format user watched movies data for MCP resource."""
        result = "# Your Watched Movies on Trakt\n\n"
        
        if not movies:
            return result + "You haven't watched any movies yet, or you need to authenticate first."
        
        for item in movies:
            movie = item.get("movie", {})
            last_watched = item.get("last_watched_at", "Unknown")
            plays = item.get("plays", 0)
            
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""
            
            result += f"- **{title}{year_str}** - Watched: {last_watched}, Plays: {plays}\n"
            
            if overview := movie.get("overview"):
                result += f"  {overview}\n"
            
            result += "\n"
            
        return result
        
    @staticmethod
    def format_checkin_response(response: Dict) -> str:
        """Format the checkin response from Trakt API.
        
        Args:
            response: The checkin response data
            
        Returns:
            Formatted response message
        """
        try:
            # Extract show and episode info
            show = response.get("show", {})
            episode = response.get("episode", {})
            
            show_title = show.get("title", "Unknown show")
            episode_title = episode.get("title", "Unknown episode")
            season = episode.get("season", 0)
            number = episode.get("number", 0)
            
            # Format the success message
            message = f"# Successfully Checked In\n\n"
            message += f"You are now checked in to **{show_title}** - S{season:02d}E{number:02d}: {episode_title}\n\n"
            
            # Add watched_at time if available
            if watched_at := response.get("watched_at"):
                # Try to format the timestamp for better readability
                try:
                    # Format the timestamp (removing the 'Z' and truncating milliseconds)
                    watched_time = watched_at.replace('Z', '').split('.')[0].replace('T', ' ')
                    message += f"Watched at: {watched_time} UTC\n\n"
                except:
                    message += f"Watched at: {watched_at}\n\n"
            
            # Add sharing info if available
            if sharing := response.get("sharing", {}):
                platforms = []
                for platform, shared in sharing.items():
                    if shared:
                        platforms.append(platform.capitalize())
                
                if platforms:
                    message += f"Shared on: {', '.join(platforms)}\n\n"
            
            # Add checkin ID if available
            if checkin_id := response.get("id"):
                message += f"Checkin ID: {checkin_id}\n"
                
            return message
            
        except Exception as e:
            # Fallback for any parsing errors
            return f"Successfully checked in to the show.\n\nDetails: {str(response)}"
            
    @staticmethod
    def format_show_search_results(results: List[Dict]) -> str:
        """Format show search results from Trakt API.
        
        Args:
            results: The search results data
            
        Returns:
            Formatted search results message
        """
        if not results:
            return "# Show Search Results\n\nNo shows found matching your query."
        
        message = "# Show Search Results\n\n"
        message += "Here are the shows matching your search query:\n\n"
        
        for index, item in enumerate(results, 1):
            show = item.get("show", {})
            
            # Extract show details
            title = show.get("title", "Unknown show")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""
            
            # Extract IDs
            ids = show.get("ids", {})
            trakt_id = ids.get("trakt", "unknown")
            
            # Format the result entry with the Trakt ID included for easy reference
            message += f"**{index}. {title}{year_str}** (ID: {trakt_id})\n"
            
            # Add overview if available
            if overview := show.get("overview"):
                # Truncate long overviews
                if len(overview) > 200:
                    overview = overview[:197] + "..."
                message += f"  {overview}\n"
            
            # Add a note about using this ID for check-ins
            message += f"  *Use this ID for check-ins: `{trakt_id}`*\n\n"
        
        # Add a tip for using the search results
        message += "\nTo check in to a show, use the `checkin_to_show` tool with the show ID, season number, and episode number."
        
        return message 