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

This code will expire in {minutes} minutes. Once you have authorized the application, your request will continue automatically.
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