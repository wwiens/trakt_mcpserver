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