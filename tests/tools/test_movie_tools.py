import pytest
import asyncio
from unittest.mock import patch, MagicMock
import time
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    fetch_user_watched_movies, search_movies,
    fetch_trending_movies, fetch_popular_movies,
    fetch_favorited_movies, fetch_played_movies, fetch_watched_movies,
    fetch_movie_comments, fetch_movie_ratings
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_fetch_user_watched_movies_authenticated():
    sample_movies = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology."
            },
            "last_watched_at": "2023-02-15T20:30:00Z",
            "plays": 3
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        future = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_user_watched_movies.return_value = future
        
        result = await fetch_user_watched_movies()
        
        assert "# Your Watched Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "Plays: 3" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_user_watched_movies_not_authenticated():
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.start_device_auth') as mock_start_auth:
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        mock_start_auth.return_value = "# Trakt Authentication Required\n\nPlease authenticate..."
        
        result = await fetch_user_watched_movies()
        
        assert "Authentication required" in result
        assert "# Trakt Authentication Required" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_not_called()
        mock_start_auth.assert_called_once()

@pytest.mark.asyncio
async def test_search_movies():
    sample_results = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
                "ids": {"trakt": "1"}
            }
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        
        future = asyncio.Future()
        future.set_result(sample_results)
        mock_client.search_movies.return_value = future
        
        result = await search_movies(query="inception")
        
        assert "# Movie Search Results" in result
        assert "Inception (2010)" in result
        assert "ID: 1" in result
        
        mock_client.search_movies.assert_called_once()
        args, kwargs = mock_client.search_movies.call_args
        assert args[0] == "inception"  # First positional arg should be the query
        assert args[1] == 10  # Second positional arg should be the limit

@pytest.mark.asyncio
async def test_fetch_trending_movies():
    sample_movies = [
        {
            "watchers": 150,
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology."
            }
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        
        future = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_trending_movies.return_value = future
        
        result = await fetch_trending_movies(limit=5)
        
        assert "# Trending Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "150 watchers" in result
        
        mock_client.get_trending_movies.assert_called_once_with(limit=5)

@pytest.mark.asyncio
async def test_fetch_movie_comments():
    sample_movie = {
        "title": "Inception",
        "year": 2010
    }
    
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This is a great movie!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123"
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        
        movie_future = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future
        
        comments_future = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_movie_comments.return_value = comments_future
        
        result = await fetch_movie_comments(movie_id="1", limit=5)
        
        assert "Movie: Inception" in result
        assert "user1" in result
        assert "This is a great movie!" in result
        
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_comments.assert_called_once_with("1", limit=5, sort="newest")

@pytest.mark.asyncio
async def test_fetch_movie_ratings():
    sample_movie = {
        "title": "Inception",
        "year": 2010
    }
    
    sample_ratings = {
        "rating": 9.0,
        "votes": 2000,
        "distribution": {
            "10": 800,
            "9": 600,
            "8": 300,
            "7": 150,
            "6": 80,
            "5": 40,
            "4": 20,
            "3": 5,
            "2": 3,
            "1": 2
        }
    }
    
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        
        movie_future = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future
        
        ratings_future = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_movie_ratings.return_value = ratings_future
        
        result = await fetch_movie_ratings(movie_id="1")
        
        assert "# Ratings for Inception" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 2000 votes" in result
        
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_called_once_with("1")

@pytest.mark.asyncio
async def test_fetch_movie_ratings_error():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        
        future = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie.return_value = future
        
        result = await fetch_movie_ratings(movie_id="1")
        
        assert "Error fetching ratings for movie ID 1" in result
        
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_not_called()
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
    fetch_user_watched_movies, search_movies,
    fetch_trending_movies, fetch_popular_movies,
    fetch_favorited_movies, fetch_played_movies, fetch_watched_movies,
    fetch_movie_comments, fetch_movie_ratings
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_fetch_user_watched_movies_authenticated():
    """Test fetching user watched movies when authenticated."""
    sample_movies = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology."
            },
            "last_watched_at": "2023-02-15T20:30:00Z",
            "plays": 3
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_user_watched_movies.return_value = future
        
        # Call the tool function
        result = await fetch_user_watched_movies()
        
        # Verify the result
        assert "# Your Watched Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "Plays: 3" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_user_watched_movies_not_authenticated():
    """Test fetching user watched movies when not authenticated."""
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.start_device_auth') as mock_start_auth:
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Mock the start_device_auth function
        mock_start_auth.return_value = "# Trakt Authentication Required\n\nPlease authenticate..."
        
        # Call the tool function
        result = await fetch_user_watched_movies()
        
        # Verify the result
        assert "Authentication required" in result
        assert "# Trakt Authentication Required" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_not_called()
        mock_start_auth.assert_called_once()

@pytest.mark.asyncio
async def test_search_movies():
    """Test searching for movies."""
    sample_results = [
        {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
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
        mock_client.search_movies.return_value = future
        
        # Call the tool function
        result = await search_movies(query="inception")
        
        # Verify the result
        assert "# Movie Search Results" in result
        assert "Inception (2010)" in result
        assert "ID: 1" in result
        
        # Verify the client methods were called
        mock_client.search_movies.assert_called_once()
        args, kwargs = mock_client.search_movies.call_args
        assert args[0] == "inception"  # First positional arg should be the query
        assert args[1] == 10  # Second positional arg should be the limit

@pytest.mark.asyncio
async def test_fetch_trending_movies():
    """Test fetching trending movies."""
    sample_movies = [
        {
            "watchers": 150,
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology."
            }
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_trending_movies.return_value = future
        
        # Call the tool function
        result = await fetch_trending_movies(limit=5)
        
        # Verify the result
        assert "# Trending Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "150 watchers" in result
        
        # Verify the client methods were called
        mock_client.get_trending_movies.assert_called_once_with(limit=5)

@pytest.mark.asyncio
async def test_fetch_movie_comments():
    """Test fetching movie comments."""
    sample_movie = {
        "title": "Inception",
        "year": 2010
    }
    
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This is a great movie!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123"
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable results
        movie_future = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future
        
        comments_future = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_movie_comments.return_value = comments_future
        
        # Call the tool function
        result = await fetch_movie_comments(movie_id="1", limit=5)
        
        # Verify the result
        assert "Movie: Inception" in result
        assert "user1" in result
        assert "This is a great movie!" in result
        
        # Verify the client methods were called
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_comments.assert_called_once_with("1", limit=5, sort="newest")

@pytest.mark.asyncio
async def test_fetch_movie_ratings():
    """Test fetching movie ratings."""
    sample_movie = {
        "title": "Inception",
        "year": 2010
    }
    
    sample_ratings = {
        "rating": 9.0,
        "votes": 2000,
        "distribution": {
            "10": 800,
            "9": 600,
            "8": 300,
            "7": 150,
            "6": 80,
            "5": 40,
            "4": 20,
            "3": 5,
            "2": 3,
            "1": 2
        }
    }
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable results
        movie_future = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future
        
        ratings_future = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_movie_ratings.return_value = ratings_future
        
        # Call the tool function
        result = await fetch_movie_ratings(movie_id="1")
        
        # Verify the result
        assert "# Ratings for Inception" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 2000 votes" in result
        
        # Verify the client methods were called
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_called_once_with("1")

@pytest.mark.asyncio
async def test_fetch_movie_ratings_error():
    """Test fetching movie ratings with an error."""
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create a future that raises an exception
        future = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie.return_value = future
        
        # Call the tool function
        result = await fetch_movie_ratings(movie_id="1")
        
        # Verify the result
        assert "Error fetching ratings for movie ID 1" in result
        
        # Verify the client methods were called
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_not_called()
