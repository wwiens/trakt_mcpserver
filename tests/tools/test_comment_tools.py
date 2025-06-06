import pytest
import asyncio
from unittest.mock import patch, MagicMock
import time
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    fetch_season_comments, fetch_episode_comments,
    fetch_comment, fetch_comment_replies
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_fetch_season_comments():
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008
    }
    
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This season was amazing!",
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
        mock_client.get_season_comments.return_value = comments_future
        
        result = await fetch_season_comments(show_id="1", season=1, limit=5)
        
        assert "Show: Breaking Bad - Season 1" in result
        assert "user1" in result
        assert "This season was amazing!" in result
        
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_season_comments.assert_called_once_with("1", 1, limit=5, sort="newest")

@pytest.mark.asyncio
async def test_fetch_episode_comments():
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008
    }
    
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This episode was incredible!",
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
        mock_client.get_episode_comments.return_value = comments_future
        
        result = await fetch_episode_comments(show_id="1", season=1, episode=1, limit=5)
        
        assert "Show: Breaking Bad - S01E01" in result
        assert "user1" in result
        assert "This episode was incredible!" in result
        
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_episode_comments.assert_called_once_with("1", 1, 1, limit=5, sort="newest")

@pytest.mark.asyncio
async def test_fetch_comment():
    sample_comment = {
        "user": {"username": "user1"},
        "created_at": "2023-01-15T20:30:00Z",
        "comment": "This is my comment!",
        "spoiler": False,
        "review": False,
        "replies": 2,
        "likes": 10,
        "id": "123"
    }
    
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        
        future = asyncio.Future()
        future.set_result(sample_comment)
        mock_client.get_comment.return_value = future
        
        result = await fetch_comment(comment_id="123")
        
        assert "# Comment by user1" in result
        assert "This is my comment!" in result
        
        mock_client.get_comment.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_fetch_comment_replies():
    sample_comment = {
        "user": {"username": "user1"},
        "created_at": "2023-01-15T20:30:00Z",
        "comment": "This is my comment!",
        "spoiler": False,
        "review": False,
        "replies": 2,
        "likes": 10,
        "id": "123"
    }
    
    sample_replies = [
        {
            "user": {"username": "user2"},
            "created_at": "2023-01-16T10:15:00Z",
            "comment": "I agree with you!",
            "spoiler": False,
            "review": False,
            "id": "124"
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        
        comment_future = asyncio.Future()
        comment_future.set_result(sample_comment)
        mock_client.get_comment.return_value = comment_future
        
        replies_future = asyncio.Future()
        replies_future.set_result(sample_replies)
        mock_client.get_comment_replies.return_value = replies_future
        
        result = await fetch_comment_replies(comment_id="123", limit=5)
        
        assert "# Comment by user1" in result
        assert "This is my comment!" in result
        assert "## Replies" in result
        assert "user2" in result
        assert "I agree with you!" in result
        
        mock_client.get_comment.assert_called_once_with("123")
        mock_client.get_comment_replies.assert_called_once_with("123", limit=5, sort="newest")
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
    fetch_season_comments, fetch_episode_comments,
    fetch_comment, fetch_comment_replies
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_fetch_season_comments():
    """Test fetching season comments."""
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008
    }
    
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This season was amazing!",
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
        show_future = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future
        
        comments_future = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_season_comments.return_value = comments_future
        
        # Call the tool function
        result = await fetch_season_comments(show_id="1", season=1, limit=5)
        
        # Verify the result
        assert "Show: Breaking Bad - Season 1" in result
        assert "user1" in result
        assert "This season was amazing!" in result
        
        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_season_comments.assert_called_once_with("1", 1, limit=5, sort="newest")

@pytest.mark.asyncio
async def test_fetch_episode_comments():
    """Test fetching episode comments."""
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008
    }
    
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This episode was incredible!",
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
        show_future = asyncio.Future()
        show_future.set_result(sample_show)
        mock_client.get_show.return_value = show_future
        
        comments_future = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_episode_comments.return_value = comments_future
        
        # Call the tool function
        result = await fetch_episode_comments(show_id="1", season=1, episode=1, limit=5)
        
        # Verify the result
        assert "Show: Breaking Bad - S01E01" in result
        assert "user1" in result
        assert "This episode was incredible!" in result
        
        # Verify the client methods were called
        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_episode_comments.assert_called_once_with("1", 1, 1, limit=5, sort="newest")

@pytest.mark.asyncio
async def test_fetch_comment():
    """Test fetching a specific comment."""
    sample_comment = {
        "user": {"username": "user1"},
        "created_at": "2023-01-15T20:30:00Z",
        "comment": "This is my comment!",
        "spoiler": False,
        "review": False,
        "replies": 2,
        "likes": 10,
        "id": "123"
    }
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable result
        future = asyncio.Future()
        future.set_result(sample_comment)
        mock_client.get_comment.return_value = future
        
        # Call the tool function
        result = await fetch_comment(comment_id="123")
        
        # Verify the result
        assert "# Comment by user1" in result
        assert "This is my comment!" in result
        
        # Verify the client methods were called
        mock_client.get_comment.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_fetch_comment_replies():
    """Test fetching replies to a comment."""
    sample_comment = {
        "user": {"username": "user1"},
        "created_at": "2023-01-15T20:30:00Z",
        "comment": "This is my comment!",
        "spoiler": False,
        "review": False,
        "replies": 2,
        "likes": 10,
        "id": "123"
    }
    
    sample_replies = [
        {
            "user": {"username": "user2"},
            "created_at": "2023-01-16T10:15:00Z",
            "comment": "I agree with you!",
            "spoiler": False,
            "review": False,
            "id": "124"
        }
    ]
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable results
        comment_future = asyncio.Future()
        comment_future.set_result(sample_comment)
        mock_client.get_comment.return_value = comment_future
        
        replies_future = asyncio.Future()
        replies_future.set_result(sample_replies)
        mock_client.get_comment_replies.return_value = replies_future
        
        # Call the tool function
        result = await fetch_comment_replies(comment_id="123", limit=5)
        
        # Verify the result
        assert "# Comment by user1" in result
        assert "This is my comment!" in result
        assert "## Replies" in result
        assert "user2" in result
        assert "I agree with you!" in result
        
        # Verify the client methods were called
        mock_client.get_comment.assert_called_once_with("123")
        mock_client.get_comment_replies.assert_called_once_with("123", limit=5, sort="newest")

@pytest.mark.asyncio
async def test_fetch_comment_string_error_handling():
    """Test fetching a comment with a string error response."""
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock to return a string error
        mock_client = mock_client_class.return_value
        
        # Create a future that returns a string error
        future = asyncio.Future()
        future.set_result("Error: The requested comment was not found.")
        mock_client.get_comment.return_value = future
        
        # Call the tool function
        result = await fetch_comment(comment_id="123")
        
        # Verify the result contains the error message
        assert "Error fetching comment 123: Error: The requested comment was not found." in result
        
        # Verify the client methods were called
        mock_client.get_comment.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_fetch_comment_replies_string_error_handling():
    """Test fetching comment replies with a string error response."""
    sample_comment = {
        "user": {"username": "user1"},
        "created_at": "2023-01-15T20:30:00Z",
        "comment": "This is my comment!",
        "spoiler": False,
        "review": False,
        "replies": 2,
        "likes": 10,
        "id": "123"
    }
    
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        
        # Create awaitable results
        comment_future = asyncio.Future()
        comment_future.set_result(sample_comment)
        mock_client.get_comment.return_value = comment_future
        
        # Create a future that returns a string error for replies
        replies_future = asyncio.Future()
        replies_future.set_result("Error: Unable to fetch replies.")
        mock_client.get_comment_replies.return_value = replies_future
        
        # Call the tool function
        result = await fetch_comment_replies(comment_id="123", limit=5)
        
        # Verify the result contains the error message
        assert "Error fetching comment replies for 123: Error: Unable to fetch replies." in result
        
        # Verify the client methods were called
        mock_client.get_comment.assert_called_once_with("123")
        mock_client.get_comment_replies.assert_called_once_with("123", limit=5, sort="newest")
