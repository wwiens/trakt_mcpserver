import pytest
import asyncio
from unittest.mock import patch, MagicMock
import time
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    get_user_watched_shows, get_trending_shows, get_popular_shows,
    get_favorited_shows, get_played_shows, get_watched_shows,
    get_show_ratings
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_get_user_watched_shows_authenticated():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
            },
            "last_watched_at": "2023-01-15T20:30:00Z",
            "plays": 5
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_user_watched_shows.return_value = future
        
        # Call the resource function
        result = await get_user_watched_shows()
        
        # Verify the result
        assert "# Your Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "Plays: 5" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_watched_shows_not_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Call the resource function
        result = await get_user_watched_shows()
        
        # Verify the result
        assert "# Authentication Required" in result
        assert "You need to authenticate with Trakt" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_not_called()

@pytest.mark.asyncio
async def test_get_trending_shows():
    sample_shows = [
        {
            "watchers": 100,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
            }
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_trending_shows.return_value = future
        
        # Call the resource function
        result = await get_trending_shows()
        
        # Verify the result
        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result
        
        # Verify the client methods were called
        mock_client.get_trending_shows.assert_called_once()

@pytest.mark.asyncio
async def test_get_popular_shows():
    sample_shows = [
        {
            "title": "Breaking Bad",
            "year": 2008,
            "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_popular_shows.return_value = future
        
        # Call the resource function
        result = await get_popular_shows()
        
        # Verify the result
        assert "# Popular Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        
        # Verify the client methods were called
        mock_client.get_popular_shows.assert_called_once()

@pytest.mark.asyncio
async def test_get_show_ratings():
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008
    }
    
    sample_ratings = {
        "rating": 9.0,
        "votes": 1000,
        "distribution": {
            "10": 500,
            "9": 300,
            "8": 100,
            "7": 50,
            "6": 20,
            "5": 15,
            "4": 10,
            "3": 3,
            "2": 1,
            "1": 1
        }
    }
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable results
        show_future = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future
        
        ratings_future = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_show_ratings.return_value = ratings_future
        
        # Call the resource function
        result = await get_show_ratings("1")
        
        # Verify the result
        assert "# Ratings for Breaking Bad" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 1000 votes" in result
        
        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_called_once_with("1")

@pytest.mark.asyncio
async def test_get_show_ratings_error_handling():
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock to raise an exception
        mock_client = mock_client_class.return_value
        
        # Create a future that raises an exception
        future = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_show.return_value = future
        
        # Call the resource function
        result = await get_show_ratings("1")
        
        # Verify the result contains an error message
        assert "Error fetching ratings for show ID 1" in result
        
        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()
import pytest
import asyncio
from unittest.mock import patch, MagicMock
import time
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    get_user_watched_shows, get_trending_shows, get_popular_shows,
    get_favorited_shows, get_played_shows, get_watched_shows,
    get_show_ratings
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_get_user_watched_shows_authenticated():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
            },
            "last_watched_at": "2023-01-15T20:30:00Z",
            "plays": 5
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_user_watched_shows.return_value = future
        
        # Call the resource function
        result = await get_user_watched_shows()
        
        # Verify the result
        assert "# Your Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "Plays: 5" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_watched_shows_not_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Call the resource function
        result = await get_user_watched_shows()
        
        # Verify the result
        assert "# Authentication Required" in result
        assert "You need to authenticate with Trakt" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_not_called()

@pytest.mark.asyncio
async def test_get_trending_shows():
    sample_shows = [
        {
            "watchers": 100,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
            }
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_trending_shows.return_value = future
        
        # Call the resource function
        result = await get_trending_shows()
        
        # Verify the result
        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result
        
        # Verify the client methods were called
        mock_client.get_trending_shows.assert_called_once()

@pytest.mark.asyncio
async def test_get_popular_shows():
    sample_shows = [
        {
            "title": "Breaking Bad",
            "year": 2008,
            "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_popular_shows.return_value = future
        
        # Call the resource function
        result = await get_popular_shows()
        
        # Verify the result
        assert "# Popular Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        
        # Verify the client methods were called
        mock_client.get_popular_shows.assert_called_once()

@pytest.mark.asyncio
async def test_get_show_ratings():
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008
    }
    
    sample_ratings = {
        "rating": 9.0,
        "votes": 1000,
        "distribution": {
            "10": 500,
            "9": 300,
            "8": 100,
            "7": 50,
            "6": 20,
            "5": 15,
            "4": 10,
            "3": 3,
            "2": 1,
            "1": 1
        }
    }
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable results
        show_future = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future
        
        ratings_future = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_show_ratings.return_value = ratings_future
        
        # Call the resource function
        result = await get_show_ratings("1")
        
        # Verify the result
        assert "# Ratings for Breaking Bad" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 1000 votes" in result
        
        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_called_once_with("1")

@pytest.mark.asyncio
async def test_get_show_ratings_error_handling():
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock to raise an exception
        mock_client = mock_client_class.return_value
        
        # Create a future that raises an exception
        future = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_show.return_value = future
        
        # Call the resource function
        result = await get_show_ratings("1")
        
        # Verify the result contains an error message
        assert "Error fetching ratings for show ID 1" in result
        
        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()
