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
    start_device_auth, check_auth_status, clear_auth,
    fetch_user_watched_shows, fetch_user_watched_movies,
    search_shows, search_movies, checkin_to_show,
    fetch_trending_shows, fetch_popular_shows,
    fetch_show_comments, fetch_movie_comments,
    fetch_show_ratings, fetch_movie_ratings
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_start_device_auth():
    device_code_response = {
        "device_code": "device_code_123",
        "user_code": "USER123",
        "verification_url": "https://trakt.tv/activate",
        "expires_in": 600,
        "interval": 5
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        future = asyncio.Future()
        future.set_result(MagicMock(
            device_code="device_code_123",
            user_code="USER123",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
            interval=5
        ))
        mock_client.get_device_code.return_value = future
        
        result = await start_device_auth()
        
        assert "# Trakt Authentication Required" in result
        assert "USER123" in result
        assert "https://trakt.tv/activate" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_code.assert_called_once()

@pytest.mark.asyncio
async def test_start_device_auth_already_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        result = await start_device_auth()
        
        assert "You are already authenticated with Trakt" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_code.assert_not_called()

@pytest.mark.asyncio
async def test_check_auth_status_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        result = await check_auth_status()
        
        assert "# Authentication Successful" in result
        assert "You are now authenticated with Trakt" in result
        
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_no_active_flow():
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        result = await check_auth_status()
        
        assert "No active authentication flow" in result
        assert "start_device_auth" in result
        
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_expired_flow():
    """Test checking auth status with expired flow."""
    expired_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) - 100,  # Expired 100 seconds ago
        "interval": 5,
        "last_poll": 0
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', expired_flow):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        result = await check_auth_status()
        
        assert "Authentication flow expired" in result
        assert "start a new one" in result
        
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_pending_authorization():
    """Test checking auth status with pending authorization."""
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10  # Last polled 10 seconds ago
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', active_flow):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        none_future = asyncio.Future()
        none_future.set_result(None)
        mock_client.get_device_token.return_value = none_future
        
        result = await check_auth_status()
        
        assert "# Authorization Pending" in result
        assert "I don't see that you've completed the authorization yet" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")

@pytest.mark.asyncio
async def test_check_auth_status_authorization_complete():
    """Test checking auth status when authorization is complete."""
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10  # Last polled 10 seconds ago
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', active_flow):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        future = asyncio.Future()
        future.set_result(MagicMock(
            access_token="access_token_123",
            refresh_token="refresh_token_123"
        ))
        mock_client.get_device_token.return_value = future
        
        result = await check_auth_status()
        
        assert "# Authentication Successful" in result
        assert "You have successfully authorized" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")

@pytest.mark.asyncio
async def test_clear_auth():
    """Test clearing authentication."""
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {"device_code": "device_code_123"}):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = True
        
        # Call the tool function
        result = await clear_auth()
        
        # Verify the result
        assert "You have been successfully logged out of Trakt" in result
        
        # Verify the client methods were called
        mock_client.clear_auth_token.assert_called_once()
        
        # Verify active_auth_flow was cleared
        from server import active_auth_flow
        assert active_auth_flow == {}

@pytest.mark.asyncio
async def test_clear_auth_not_authenticated():
    """Test clearing authentication when not authenticated."""
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = False
        
        # Call the tool function
        result = await clear_auth()
        
        # Verify the result
        assert "You were not authenticated with Trakt" in result
        
        # Verify the client methods were called
        mock_client.clear_auth_token.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_user_watched_shows_authenticated():
    """Test fetching user watched shows when authenticated."""
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
        
        # Call the tool function
        result = await fetch_user_watched_shows()
        
        # Verify the result
        assert "# Your Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "Plays: 5" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_user_watched_shows_not_authenticated():
    """Test fetching user watched shows when not authenticated."""
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.start_device_auth') as mock_start_auth:
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Mock the start_device_auth function
        mock_start_auth.return_value = "# Trakt Authentication Required\n\nPlease authenticate..."
        
        # Call the tool function
        result = await fetch_user_watched_shows()
        
        # Verify the result
        assert "Authentication required" in result
        assert "# Trakt Authentication Required" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_not_called()
        mock_start_auth.assert_called_once()

@pytest.mark.asyncio
async def test_search_shows():
    """Test searching for shows."""
    sample_results = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
                "ids": {"trakt": "1"}
            }
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_shows.return_value = future
        
        # Call the tool function
        result = await search_shows(query="breaking bad")
        
        # Verify the result
        assert "# Show Search Results" in result
        assert "Breaking Bad (2008)" in result
        assert "ID: 1" in result
        
        # Verify the client methods were called - adjust the assertion to match how the method is actually called
        mock_client.search_shows.assert_called_once()
        args, kwargs = mock_client.search_shows.call_args
        assert args[0] == "breaking bad"  # First positional arg should be the query
        assert args[1] == 10  # Second positional arg should be the limit

@pytest.mark.asyncio
async def test_checkin_to_show_authenticated():
    """Test checking in to a show when authenticated."""
    sample_response = {
        "id": 123456,
        "watched_at": "2023-05-10T20:30:00Z",
        "show": {
            "title": "Breaking Bad",
            "year": 2008
        },
        "episode": {
            "season": 1,
            "number": 1,
            "title": "Pilot"
        }
    }
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_response)
        mock_client.checkin_to_show.return_value = future
        
        # Call the tool function
        result = await checkin_to_show(
            season=1,
            episode=1,
            show_id="1"
        )
        
        # Verify the result
        assert "# Successfully Checked In" in result
        assert "Breaking Bad" in result
        assert "S01E01" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.checkin_to_show.assert_called_once_with(
            episode_season=1,
            episode_number=1,
            show_id="1",
            show_title=None,
            show_year=None,
            message="",
            share_twitter=False,
            share_mastodon=False,
            share_tumblr=False
        )

@pytest.mark.asyncio
async def test_checkin_to_show_not_authenticated():
    """Test checking in to a show when not authenticated."""
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.start_device_auth') as mock_start_auth:
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Mock the start_device_auth function
        mock_start_auth.return_value = "# Trakt Authentication Required\n\nPlease authenticate..."
        
        # Call the tool function
        result = await checkin_to_show(
            season=1,
            episode=1,
            show_id="1"
        )
        
        # Verify the result
        assert "Authentication required" in result
        assert "# Trakt Authentication Required" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.checkin_to_show.assert_not_called()
        mock_start_auth.assert_called_once()

@pytest.mark.asyncio
async def test_checkin_to_show_missing_info():
    """Test checking in to a show with missing information."""
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        # Call the tool function with missing show_id and show_title
        result = await checkin_to_show(
            season=1,
            episode=1
        )
        
        # Verify the result
        assert "Error: You must provide either a show_id or a show_title" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.checkin_to_show.assert_not_called()

@pytest.mark.asyncio
async def test_fetch_trending_shows():
    """Test fetching trending shows."""
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
        
        # Call the tool function
        result = await fetch_trending_shows(limit=5)
        
        # Verify the result
        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result
        
        # Verify the client methods were called
        mock_client.get_trending_shows.assert_called_once_with(limit=5)

@pytest.mark.asyncio
async def test_fetch_show_comments():
    """Test fetching show comments."""
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008
    }
    
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This is a great show!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123"
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        
        show_future = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future
        
        comments_future = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_show_comments.return_value = comments_future
        
        result = await fetch_show_comments(show_id="1", limit=5)
        
        assert "# Comments for Show: Breaking Bad" in result
        assert "user1" in result
        assert "This is a great show!" in result
        
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_comments.assert_called_once_with("1", limit=5, sort="newest")

@pytest.mark.asyncio
async def test_fetch_show_ratings():
    """Test fetching show ratings."""
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
        
        # Call the tool function
        result = await fetch_show_ratings(show_id="1")
        
        # Verify the result
        assert "# Ratings for Breaking Bad" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 1000 votes" in result
        
        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_called_once_with("1")

@pytest.mark.asyncio
async def test_fetch_show_ratings_error():
    """Test fetching show ratings with an error."""
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create a future that raises an exception
        future = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_show.return_value = future
        
        # Call the tool function
        result = await fetch_show_ratings(show_id="1")
        
        # Verify the result
        assert "Error fetching ratings for show ID 1" in result
        
        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()
