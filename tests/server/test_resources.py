import pytest
import asyncio
from unittest.mock import patch
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    get_auth_status, get_user_watched_shows, get_user_watched_movies,
    get_trending_shows, get_popular_shows, get_trending_movies,
    get_show_ratings, get_movie_ratings
)

@pytest.mark.asyncio
async def test_get_auth_status_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        mock_client.get_token_expiry.return_value = int(time.time()) + 3600  # 1 hour from now
        
        result = await get_auth_status()
        
        assert "# Authentication Status" in result
        assert "You are authenticated with Trakt" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_token_expiry.assert_called_once()

@pytest.mark.asyncio
async def test_get_auth_status_not_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        result = await get_auth_status()
        
        assert "# Authentication Status" in result
        assert "You are not authenticated with Trakt" in result
        assert "start_device_auth" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_token_expiry.assert_not_called()

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
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_user_watched_shows.return_value = future
        
        result = await get_user_watched_shows()
        
        assert "# Your Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "Plays: 5" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_watched_shows_not_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        result = await get_user_watched_shows()
        
        assert "# Authentication Required" in result
        assert "You need to authenticate with Trakt" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_shows.assert_not_called()

@pytest.mark.asyncio
async def test_get_user_watched_movies_authenticated():
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
        
        result = await get_user_watched_movies()
        
        assert "# Your Watched Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "Plays: 3" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_user_watched_movies.assert_called_once()

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
        mock_client = mock_client_class.return_value
        
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_trending_shows.return_value = future
        
        result = await get_trending_shows()
        
        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result
        
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
        mock_client = mock_client_class.return_value
        
        future = asyncio.Future()
        future.set_result(sample_shows)
        mock_client.get_popular_shows.return_value = future
        
        result = await get_popular_shows()
        
        assert "# Popular Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        
        mock_client.get_popular_shows.assert_called_once()

@pytest.mark.asyncio
async def test_get_trending_movies():
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
        
        result = await get_trending_movies()
        
        assert "# Trending Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "150 watchers" in result
        
        mock_client.get_trending_movies.assert_called_once()

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
        mock_client = mock_client_class.return_value
        
        show_future = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future
        
        ratings_future = asyncio.Future()
        ratings_future.set_result(sample_ratings)
        mock_client.get_show_ratings.return_value = ratings_future
        
        result = await get_show_ratings("1")
        
        assert "# Ratings for Breaking Bad" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 1000 votes" in result
        
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_called_once_with("1")

@pytest.mark.asyncio
async def test_get_movie_ratings():
    sample_movie = {
        "title": "Inception",
        "year": 2010
    }
    
    sample_ratings = {
        "rating": 8.5,
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
        
        result = await get_movie_ratings("1")
        
        assert "# Ratings for Inception" in result
        assert "**Average Rating:** 8.50/10" in result
        assert "from 2000 votes" in result
        
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_called_once_with("1")

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

@pytest.mark.asyncio
async def test_get_movie_ratings_error_handling():
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock to raise an exception
        mock_client = mock_client_class.return_value
        
        # Create a future that raises an exception
        future = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie.return_value = future
        
        # Call the resource function
        result = await get_movie_ratings("1")
        
        # Verify the result contains an error message
        assert "Error fetching ratings for movie ID 1" in result
        
        # Verify the client methods were called
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_not_called()
