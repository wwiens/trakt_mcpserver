import os
from typing import Dict, List, Any, Optional
import httpx
from dotenv import load_dotenv

from config import TRAKT_ENDPOINTS, DEFAULT_LIMIT
from utils import handle_api_errors

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