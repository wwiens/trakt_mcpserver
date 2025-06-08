from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


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
    def from_api_response(cls, api_data: Dict[str, Any]) -> "TraktPopularShow":
        """Create a TraktPopularShow instance from raw API data."""
        return cls(show=TraktShow(**api_data))


class TraktPopularMovie(BaseModel):
    """Represents a popular movie from Trakt API."""
    movie: TraktMovie = Field(description="The movie information")
    
    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> "TraktPopularMovie":
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
    seasons: Optional[List[Dict[str, Any]]] = None
    plays: int


class FormatHelper:
    """Helper class for formatting Trakt data for MCP responses."""
    
    @staticmethod
    def format_trending_shows(shows: List[Dict[str, Any]]) -> str:
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
    def format_popular_shows(shows: List[Dict[str, Any]]) -> str:
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
    def format_favorited_shows(shows: List[Dict[str, Any]]) -> str:
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
    def format_played_shows(shows: List[Dict[str, Any]]) -> str:
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
    def format_watched_shows(shows: List[Dict[str, Any]]) -> str:
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
    def format_trending_movies(movies: List[Dict[str, Any]]) -> str:
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
    def format_popular_movies(movies: List[Dict[str, Any]]) -> str:
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
    def format_favorited_movies(movies: List[Dict[str, Any]]) -> str:
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
    def format_played_movies(movies: List[Dict[str, Any]]) -> str:
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
    def format_watched_movies(movies: List[Dict[str, Any]]) -> str:
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
    def format_user_watched_shows(shows: List[Dict[str, Any]]) -> str:
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
    def format_user_watched_movies(movies: List[Dict[str, Any]]) -> str:
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
    def format_checkin_response(response: Dict[str, Any]) -> str:
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
                platforms: list[str] = []
                for platform, shared in sharing.items():
                    if shared:
                        platforms.append(platform.capitalize())
                
                if platforms:
                    message += f"Shared on: {', '.join(platforms)}\n\n"
            
            # Add checkin ID if available
            if checkin_id := response.get("id"):
                message += f"Checkin ID: {checkin_id}\n"
                
            return message
            
        except Exception:
            # Fallback for any parsing errors
            return f"Successfully checked in to the show.\n\nDetails: {str(response)}"
            
    @staticmethod
    def format_show_search_results(results: List[Dict[str, Any]]) -> str:
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
        
    @staticmethod
    def format_movie_search_results(results: List[Dict[str, Any]]) -> str:
        """Format movie search results from Trakt API."""
        if not results:
            return "# Movie Search Results\n\nNo movies found matching your query."
        
        message = "# Movie Search Results\n\n"
        message += "Here are the movies matching your search query:\n\n"
        
        for index, item in enumerate(results, 1):
            movie = item.get("movie", {})
            
            title = movie.get("title", "Unknown movie")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""
            
            ids = movie.get("ids", {})
            trakt_id = ids.get("trakt", "unknown")
            
            message += f"**{index}. {title}{year_str}** (ID: {trakt_id})\n"
            
            if overview := movie.get("overview"):
                if len(overview) > 200:
                    overview = overview[:197] + "..."
                message += f"  {overview}\n"
            
            message += f"  *Use this ID for comments: `{trakt_id}`*\n\n"
        
        message += "\nTo view comments for a movie, use the `fetch_movie_comments` tool with the movie ID."
        
        return message
        
    @staticmethod
    def format_show_ratings(ratings: Dict[str, Any], show_title: str = "Unknown show") -> str:
        """Format show ratings data for MCP resource.
        
        Args:
            ratings: The ratings data from Trakt API
            show_title: The title of the show
            
        Returns:
            Formatted markdown text with ratings information
        """
        result = f"# Ratings for {show_title}\n\n"
        
        if not ratings:
            return result + "No ratings data available."
        
        # Extract rating data
        average_rating = ratings.get("rating", 0)
        votes = ratings.get("votes", 0)
        distribution = ratings.get("distribution", {})
        
        # Format average rating with 2 decimal places
        result += f"**Average Rating:** {average_rating:.2f}/10 from {votes} votes\n\n"
        
        # Add distribution if available
        if distribution:
            result += "## Rating Distribution\n\n"
            result += "| Rating | Votes | Percentage |\n"
            result += "|--------|-------|------------|\n"
            
            # Calculate percentages for each rating
            for rating in range(10, 0, -1):  # 10 down to 1
                rating_str = str(rating)
                count = distribution.get(rating_str, 0)
                percentage = (count / votes * 100) if votes > 0 else 0
                
                result += f"| {rating}/10 | {count} | {percentage:.1f}% |\n"
        
        return result
        
    @staticmethod
    def format_movie_ratings(ratings: Dict[str, Any], movie_title: str = "Unknown movie") -> str:
        """Format movie ratings data for MCP resource.
        
        Args:
            ratings: The ratings data from Trakt API
            movie_title: The title of the movie
            
        Returns:
            Formatted markdown text with ratings information
        """
        result = f"# Ratings for {movie_title}\n\n"
        
        if not ratings:
            return result + "No ratings data available."
        
        # Extract rating data
        average_rating = ratings.get("rating", 0)
        votes = ratings.get("votes", 0)
        distribution = ratings.get("distribution", {})
        
        # Format average rating with 2 decimal places
        result += f"**Average Rating:** {average_rating:.2f}/10 from {votes} votes\n\n"
        
        # Add distribution if available
        if distribution:
            result += "## Rating Distribution\n\n"
            result += "| Rating | Votes | Percentage |\n"
            result += "|--------|-------|------------|\n"
            
            # Calculate percentages for each rating
            for rating in range(10, 0, -1):  # 10 down to 1
                rating_str = str(rating)
                count = distribution.get(rating_str, 0)
                percentage = (count / votes * 100) if votes > 0 else 0
                
                result += f"| {rating}/10 | {count} | {percentage:.1f}% |\n"
        
        return result
        
    @staticmethod
    def format_comments(comments: List[Dict[str, Any]], title: str, show_spoilers: bool = False) -> str:
        """Format comments for MCP resource."""
        result = f"# Comments for {title}\n\n"
        
        if show_spoilers:
            result += "**Note: Showing all spoilers**\n\n"
        else:
            result += "**Note: Spoilers are hidden. Use `show_spoilers=True` to view them.**\n\n"
        
        if not comments:
            return result + "No comments found."
        
        for comment in comments:
            username = comment.get("user", {}).get("username", "Anonymous")
            created_at = comment.get("created_at", "Unknown date")
            comment_text = comment.get("comment", "")
            spoiler = comment.get("spoiler", False)
            review = comment.get("review", False)
            replies = comment.get("replies", 0)
            likes = comment.get("likes", 0)
            comment_id = comment.get("id", "")
            
            try:
                created_time = created_at.replace('Z', '').split('.')[0].replace('T', ' ')
            except:
                created_time = created_at
            
            comment_type = ""
            if review:
                comment_type = " [REVIEW]"
            if spoiler:
                comment_type += " [SPOILER]"
            
            result += f"### {username}{comment_type} - {created_time}\n"
            
            if (spoiler or "[spoiler]" in comment_text) and not show_spoilers:
                result += f"**⚠️ SPOILER WARNING ⚠️**\n\n"
                result += f"*This comment contains spoilers. Use `show_spoilers=True` to view it.*\n\n"
            else:
                if show_spoilers:
                    comment_text = comment_text.replace("[spoiler]", "")
                    comment_text = comment_text.replace("[/spoiler]", "")
                    
                result += f"{comment_text}\n\n"
            
            result += f"*Likes: {likes} | Replies: {replies} | ID: {comment_id}*\n\n"
            result += "---\n\n"
        
        return result

    @staticmethod
    def format_comment(comment: Dict[str, Any], with_replies: bool = False, replies: Optional[List[Dict[str, Any]]] = None, show_spoilers: bool = False) -> str:
        """Format a single comment with optional replies."""
        username = comment.get("user", {}).get("username", "Anonymous")
        created_at = comment.get("created_at", "Unknown date")
        comment_text = comment.get("comment", "")
        spoiler = comment.get("spoiler", False)
        review = comment.get("review", False)
        replies_count = comment.get("replies", 0)
        likes = comment.get("likes", 0)
        comment_id = comment.get("id", "")
        
        try:
            created_time = created_at.replace('Z', '').split('.')[0].replace('T', ' ')
        except:
            created_time = created_at
        
        comment_type = ""
        if review:
            comment_type = " [REVIEW]"
        if spoiler:
            comment_type += " [SPOILER]"
        
        result = f"# Comment by {username}{comment_type}\n\n"
        
        if show_spoilers:
            result += "**Note: Showing all spoilers**\n\n"
        else:
            result += "**Note: Spoilers are hidden. Use `show_spoilers=True` to view them.**\n\n"
            
        result += f"**Posted:** {created_time}\n\n"
        
        if (spoiler or "[spoiler]" in comment_text) and not show_spoilers:
            result += f"**⚠️ SPOILER WARNING ⚠️**\n\n"
            result += f"*This comment contains spoilers. Use `show_spoilers=True` to view it.*\n\n"
        else:
            if show_spoilers:
                comment_text = comment_text.replace("[spoiler]", "")
                comment_text = comment_text.replace("[/spoiler]", "")
                
            result += f"{comment_text}\n\n"
        
        result += f"*Likes: {likes} | Replies: {replies_count} | ID: {comment_id}*\n\n"
        
        if with_replies and replies:
            result += "## Replies\n\n"
            
            for reply in replies:
                reply_username = reply.get("user", {}).get("username", "Anonymous")
                reply_created_at = reply.get("created_at", "Unknown date")
                reply_text = reply.get("comment", "")
                reply_spoiler = reply.get("spoiler", False)
                reply_id = reply.get("id", "")
                
                try:
                    reply_time = reply_created_at.replace('Z', '').split('.')[0].replace('T', ' ')
                except:
                    reply_time = reply_created_at
                
                reply_type = ""
                if reply.get("review", False):
                    reply_type = " [REVIEW]"
                if reply_spoiler:
                    reply_type += " [SPOILER]"
                    
                result += f"### {reply_username}{reply_type} - {reply_time}\n"
                
                if (reply_spoiler or "[spoiler]" in reply_text) and not show_spoilers:
                    result += f"**⚠️ SPOILER WARNING ⚠️**\n\n"
                    result += f"*This reply contains spoilers. Use `show_spoilers=True` to view it.*\n\n"
                else:
                    if show_spoilers:
                        reply_text = reply_text.replace("[spoiler]", "")
                        reply_text = reply_text.replace("[/spoiler]", "")
                        
                    result += f"{reply_text}\n\n"
                
                result += f"*ID: {reply_id}*\n\n"
                result += "---\n\n"
        
        return result
