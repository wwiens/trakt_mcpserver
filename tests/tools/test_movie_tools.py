import pytest
import asyncio
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    fetch_user_watched_movies, search_movies,
    fetch_trending_movies, fetch_movie_comments, fetch_movie_ratings
)

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
        args, _ = mock_client.search_movies.call_args
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

@pytest.mark.asyncio
async def test_fetch_movie_comments_string_error_handling():
    """Test fetching movie comments with a string error response."""
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock to return a string error
        mock_client = mock_client_class.return_value
        
        # Create a future that returns a string error
        movie_future = asyncio.Future()
        movie_future.set_result("Error: The requested movie was not found.")
        mock_client.get_movie.return_value = movie_future
        
        # Call the tool function
        result = await fetch_movie_comments(movie_id="1", limit=5)
        
        # Verify the result contains the error message
        assert "Error fetching comments for Movie ID: 1: Error: The requested movie was not found." in result
        
        # Verify the client methods were called
        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_comments.assert_not_called()
