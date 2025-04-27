import os
import time
import json
from typing import Dict, List, Any, Optional
import httpx
from dotenv import load_dotenv

from config import TRAKT_ENDPOINTS, DEFAULT_LIMIT
from utils import handle_api_errors
from models import TraktDeviceCode, TraktAuthToken

# User authentication token storage path
AUTH_TOKEN_FILE = "auth_token.json"

class TraktClient:
    """Client for interacting with the Trakt API."""
    
    BASE_URL = "https://api.trakt.tv"
    
    def __init__(self):
        """Initialize the Trakt API client with credentials from environment variables."""
        load_dotenv()
        self.client_id = os.getenv("TRAKT_CLIENT_ID")
        self.client_secret = os.getenv("TRAKT_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Trakt API credentials not found. Please check your .env file.")
        
        self.headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id,
        }
        
        # Try to load auth token if exists
        self.auth_token = self._load_auth_token()
        if self.auth_token:
            self._update_headers_with_token()
    
    def _update_headers_with_token(self):
        """Update headers with authentication token."""
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token.access_token}"
    
    def _load_auth_token(self) -> Optional[TraktAuthToken]:
        """Load authentication token from storage."""
        if os.path.exists(AUTH_TOKEN_FILE):
            try:
                with open(AUTH_TOKEN_FILE, "r") as f:
                    token_data = json.load(f)
                    return TraktAuthToken(**token_data)
            except Exception as e:
                print(f"Error loading auth token: {e}")
        return None
    
    def _save_auth_token(self, token: TraktAuthToken):
        """Save authentication token to storage."""
        with open(AUTH_TOKEN_FILE, "w") as f:
            f.write(json.dumps(token.dict()))
    
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        if not self.auth_token:
            return False
        
        # Check if token is expired
        current_time = int(time.time())
        token_expiry = self.auth_token.created_at + self.auth_token.expires_in
        return current_time < token_expiry
    
    def get_token_expiry(self) -> Optional[int]:
        """Get the expiry timestamp of the current token."""
        if not self.auth_token:
            return None
        return self.auth_token.created_at + self.auth_token.expires_in
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an authenticated request to the Trakt API.
        
        Args:
            endpoint: The API endpoint to request (without the base URL)
            params: Optional query parameters
            
        Returns:
            The JSON response data
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def _post_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the Trakt API.
        
        Args:
            endpoint: The API endpoint to request (without the base URL)
            data: The data to send
            
        Returns:
            The JSON response data
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    @handle_api_errors
    async def get_device_code(self) -> TraktDeviceCode:
        """Get a device code for authentication.
        
        Returns:
            Device code response from Trakt
        """
        data = {
            "client_id": self.client_id,
        }
        response = await self._post_request(TRAKT_ENDPOINTS["device_code"], data)
        return TraktDeviceCode(**response)
    
    @handle_api_errors
    async def get_device_token(self, device_code: str) -> Optional[TraktAuthToken]:
        """Exchange device code for an access token.
        
        Args:
            device_code: The device code to exchange
            
        Returns:
            Authentication token or None if not yet authorized
        """
        data = {
            "code": device_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = await self._post_request(TRAKT_ENDPOINTS["device_token"], data)
            token = TraktAuthToken(**response)
            self.auth_token = token
            self._save_auth_token(token)
            self._update_headers_with_token()
            return token
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # User hasn't authorized yet
                return None
            raise
    
    @handle_api_errors
    async def get_user_watched_shows(self) -> List[Dict[str, Any]]:
        """Get shows watched by the authenticated user.
        
        Returns:
            List of shows watched by the user
        """
        if not self.is_authenticated():
            return []
        
        return await self._make_request(TRAKT_ENDPOINTS["user_watched_shows"])
    
    @handle_api_errors
    async def get_trending_shows(self, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Get trending shows from Trakt.
        
        Args:
            limit: Maximum number of shows to return
            
        Returns:
            List of trending shows data
        """
        return await self._make_request(TRAKT_ENDPOINTS["shows_trending"], params={"limit": limit})
    
    @handle_api_errors
    async def get_popular_shows(self, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Get popular shows from Trakt.
        
        Args:
            limit: Maximum number of shows to return
            
        Returns:
            List of popular shows data
        """
        return await self._make_request(TRAKT_ENDPOINTS["shows_popular"], params={"limit": limit})
    
    @handle_api_errors
    async def get_favorited_shows(self, limit: int = DEFAULT_LIMIT, period: str = "weekly") -> List[Dict[str, Any]]:
        """Get favorited shows from Trakt.
        
        Args:
            limit: Maximum number of shows to return
            period: Time period for favorite calculation (daily, weekly, monthly, yearly, all)
            
        Returns:
            List of favorited shows data
        """
        return await self._make_request(TRAKT_ENDPOINTS["shows_favorited"], params={"limit": limit, "period": period})
    
    @handle_api_errors
    async def get_played_shows(self, limit: int = DEFAULT_LIMIT, period: str = "weekly") -> List[Dict[str, Any]]:
        """Get played shows from Trakt.
        
        Args:
            limit: Maximum number of shows to return
            period: Time period for most played (daily, weekly, monthly, yearly, all)
            
        Returns:
            List of most played shows data
        """
        return await self._make_request(TRAKT_ENDPOINTS["shows_played"], params={"limit": limit, "period": period})
    
    @handle_api_errors
    async def get_watched_shows(self, limit: int = DEFAULT_LIMIT, period: str = "weekly") -> List[Dict[str, Any]]:
        """Get watched shows from Trakt.
        
        Args:
            limit: Maximum number of shows to return
            period: Time period for most watched (daily, weekly, monthly, yearly, all)
            
        Returns:
            List of most watched shows data
        """
        return await self._make_request(TRAKT_ENDPOINTS["shows_watched"], params={"limit": limit, "period": period})
    
    @handle_api_errors
    async def get_trending_movies(self, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Get trending movies from Trakt.
        
        Args:
            limit: Maximum number of movies to return
            
        Returns:
            List of trending movies data
        """
        return await self._make_request(TRAKT_ENDPOINTS["movies_trending"], params={"limit": limit})
    
    @handle_api_errors
    async def get_popular_movies(self, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Get popular movies from Trakt.
        
        Args:
            limit: Maximum number of movies to return
            
        Returns:
            List of popular movies data
        """
        return await self._make_request(TRAKT_ENDPOINTS["movies_popular"], params={"limit": limit})
    
    @handle_api_errors
    async def get_favorited_movies(self, limit: int = DEFAULT_LIMIT, period: str = "weekly") -> List[Dict[str, Any]]:
        """Get favorited movies from Trakt.
        
        Args:
            limit: Maximum number of movies to return
            period: Time period for favorite calculation (daily, weekly, monthly, yearly, all)
            
        Returns:
            List of favorited movies data
        """
        return await self._make_request(TRAKT_ENDPOINTS["movies_favorited"], params={"limit": limit, "period": period})
    
    @handle_api_errors
    async def get_played_movies(self, limit: int = DEFAULT_LIMIT, period: str = "weekly") -> List[Dict[str, Any]]:
        """Get played movies from Trakt.
        
        Args:
            limit: Maximum number of movies to return
            period: Time period for most played (daily, weekly, monthly, yearly, all)
            
        Returns:
            List of most played movies data
        """
        return await self._make_request(TRAKT_ENDPOINTS["movies_played"], params={"limit": limit, "period": period})
    
    @handle_api_errors
    async def get_watched_movies(self, limit: int = DEFAULT_LIMIT, period: str = "weekly") -> List[Dict[str, Any]]:
        """Get watched movies from Trakt.
        
        Args:
            limit: Maximum number of movies to return
            period: Time period for most watched (daily, weekly, monthly, yearly, all)
            
        Returns:
            List of most watched movies data
        """
        return await self._make_request(TRAKT_ENDPOINTS["movies_watched"], params={"limit": limit, "period": period})
    
    def clear_auth_token(self) -> bool:
        """Clear the authentication token.
        
        Returns:
            True if token was cleared, False if there was no token
        """
        if not self.auth_token:
            return False
            
        # Remove authorization header
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
            
        # Clear token object
        self.auth_token = None
        
        # Remove saved token file
        if os.path.exists(AUTH_TOKEN_FILE):
            os.remove(AUTH_TOKEN_FILE)
            
        return True
        
    @handle_api_errors
    async def get_user_watched_movies(self) -> List[Dict[str, Any]]:
        """Get movies watched by the authenticated user.
        
        Returns:
            List of movies watched by the user
        """
        if not self.is_authenticated():
            return []
        
        return await self._make_request(TRAKT_ENDPOINTS["user_watched_movies"])
        
    @handle_api_errors
    async def checkin_to_show(self, episode_season: int, episode_number: int, show_id: str = None, 
                            show_title: str = None, show_year: int = None, message: str = "", 
                            share_twitter: bool = False, share_mastodon: bool = False, share_tumblr: bool = False) -> Dict[str, Any]:
        """Check in to a show episode the user is currently watching.
        
        Args:
            episode_season: Season number
            episode_number: Episode number
            show_id: Trakt ID for the show (optional if show_title is provided)
            show_title: Title of the show (optional if show_id is provided)
            show_year: Year the show was released (optional, used with show_title)
            message: Optional message to include with the checkin
            share_twitter: Whether to share on Twitter
            share_mastodon: Whether to share on Mastodon
            share_tumblr: Whether to share on Tumblr
            
        Returns:
            The checkin response from Trakt
            
        Raises:
            ValueError: If the user is not authenticated or if insufficient show information is provided
        """
        if not self.is_authenticated():
            raise ValueError("You must be authenticated to check in to a show")
        
        if not show_id and not show_title:
            raise ValueError("Either show_id or show_title must be provided")
        
        # Prepare show data
        show_data = {"ids": {}} if not show_title else {"title": show_title}
        
        # Add show ID if provided
        if show_id:
            show_data["ids"]["trakt"] = show_id
            
        # Add year if provided
        if show_year:
            show_data["year"] = show_year
        
        # Prepare episode data
        episode_data = {
            "season": episode_season,
            "number": episode_number
        }
        
        # Prepare sharing data if any sharing options are enabled
        if share_twitter or share_mastodon or share_tumblr:
            sharing_data = {
                "twitter": share_twitter,
                "mastodon": share_mastodon,
                "tumblr": share_tumblr
            }
        else:
            sharing_data = None
        
        # Prepare checkin data
        data = {
            "episode": episode_data,
            "show": show_data
        }
        
        # Add optional fields if provided
        if message:
            data["message"] = message
            
        if sharing_data:
            data["sharing"] = sharing_data
            
        # Make the checkin request    
        return await self._post_request(TRAKT_ENDPOINTS["checkin"], data)
        
    @handle_api_errors
    async def search_shows(self, query: str, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Search for shows on Trakt.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of show search results
        """
        # Construct search endpoint with 'show' type filter
        search_endpoint = f"{TRAKT_ENDPOINTS['search']}/show"
        
        # Make the search request
        return await self._make_request(search_endpoint, params={
            "query": query,
            "limit": limit
        }) 
        
    @handle_api_errors
    async def search_movies(self, query: str, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Search for movies on Trakt."""
        search_endpoint = f"{TRAKT_ENDPOINTS['search']}/movie"
        return await self._make_request(search_endpoint, params={
            "query": query,
            "limit": limit
        })
        
    @handle_api_errors
    async def get_movie_comments(self, movie_id: str, limit: int = DEFAULT_LIMIT, page: int = 1, sort: str = "newest") -> List[Dict[str, Any]]:
        """Get comments for a movie.
    
        Args:
            movie_id: Trakt ID of the movie
            limit: Maximum number of comments to return
            page: Page number for pagination
            sort: How to sort comments (newest, oldest, likes, replies, highest, lowest, plays, watched)
        """
        endpoint = TRAKT_ENDPOINTS["comments_movie"].replace(":id", movie_id).replace(":sort", sort)
        return await self._make_request(endpoint, params={"limit": limit, "page": page})

    @handle_api_errors
    async def get_show_comments(self, show_id: str, limit: int = DEFAULT_LIMIT, page: int = 1, sort: str = "newest") -> List[Dict[str, Any]]:
        """Get comments for a show."""
        endpoint = TRAKT_ENDPOINTS["comments_show"].replace(":id", show_id).replace(":sort", sort)
        return await self._make_request(endpoint, params={"limit": limit, "page": page})

    @handle_api_errors
    async def get_season_comments(self, show_id: str, season: int, limit: int = DEFAULT_LIMIT, page: int = 1, sort: str = "newest") -> List[Dict[str, Any]]:
        """Get comments for a season."""
        endpoint = TRAKT_ENDPOINTS["comments_season"].replace(":id", show_id).replace(":season", str(season)).replace(":sort", sort)
        return await self._make_request(endpoint, params={"limit": limit, "page": page})

    @handle_api_errors
    async def get_episode_comments(self, show_id: str, season: int, episode: int, limit: int = DEFAULT_LIMIT, page: int = 1, sort: str = "newest") -> List[Dict[str, Any]]:
        """Get comments for an episode."""
        endpoint = TRAKT_ENDPOINTS["comments_episode"].replace(":id", show_id).replace(":season", str(season)).replace(":episode", str(episode)).replace(":sort", sort)
        return await self._make_request(endpoint, params={"limit": limit, "page": page})

    @handle_api_errors
    async def get_comment(self, comment_id: str) -> Dict[str, Any]:
        """Get a specific comment."""
        endpoint = TRAKT_ENDPOINTS["comment"].replace(":id", comment_id)
        return await self._make_request(endpoint)

    @handle_api_errors
    async def get_comment_replies(self, comment_id: str, limit: int = DEFAULT_LIMIT, page: int = 1, sort: str = "newest") -> List[Dict[str, Any]]:
        """Get replies for a comment."""
        endpoint = TRAKT_ENDPOINTS["comment_replies"].replace(":id", comment_id).replace(":sort", sort)
        return await self._make_request(endpoint, params={"limit": limit, "page": page})

    @handle_api_errors
    async def get_movie(self, movie_id: str) -> Dict[str, Any]:
        """Get details for a specific movie."""
        endpoint = f"/movies/{movie_id}"
        return await self._make_request(endpoint)

    @handle_api_errors
    async def get_show(self, show_id: str) -> Dict[str, Any]:
        """Get details for a specific show."""
        endpoint = f"/shows/{show_id}"
        return await self._make_request(endpoint)
