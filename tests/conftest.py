import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from fastmcp.client import Client

from models import TraktAuthToken


@pytest.fixture(scope="session")
async def mcp_server():
    """Start the MCP server for testing and tear down after tests."""
    server_process = subprocess.Popen(
        ["python", "-m", "mcp", "dev", "server.py"], env={"PORT": "8000"}
    )

    time.sleep(2)

    yield

    server_process.terminate()
    server_process.wait()


@pytest.fixture
async def client(mcp_server: None):
    """Create a client connection to the MCP server."""
    async with Client("http://localhost:8000/sse") as client:
        yield client


@pytest.fixture
def mock_trakt_client():
    """Create a mock TraktClient for testing."""
    with patch("server.TraktClient") as mock_client:
        # Configure the mock client
        instance = mock_client.return_value
        instance.is_authenticated.return_value = True
        yield instance


@pytest.fixture
def mock_auth_token():
    """Create a mock auth token for testing."""
    return TraktAuthToken(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )


@pytest.fixture
def sample_show_data():
    """Sample show data for testing."""
    return {
        "title": "Breaking Bad",
        "year": 2008,
        "ids": {
            "trakt": "1",
            "slug": "breaking-bad",
            "tvdb": "81189",
            "imdb": "tt0903747",
            "tmdb": "1396",
        },
        "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine.",
    }


@pytest.fixture
def sample_movie_data():
    """Sample movie data for testing."""
    return {
        "title": "Inception",
        "year": 2010,
        "ids": {
            "trakt": "1",
            "slug": "inception-2010",
            "imdb": "tt1375666",
            "tmdb": "27205",
        },
        "overview": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
    }


@pytest.fixture
def sample_trending_shows():
    """Sample trending shows data for testing."""
    return [
        {
            "watchers": 100,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": "1"},
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            },
        },
        {
            "watchers": 80,
            "show": {
                "title": "Stranger Things",
                "year": 2016,
                "ids": {"trakt": "2"},
                "overview": "When a young boy disappears, his mother, a police chief, and his friends must confront terrifying forces.",
            },
        },
    ]


@pytest.fixture
def sample_trending_movies():
    """Sample trending movies data for testing."""
    return [
        {
            "watchers": 150,
            "movie": {
                "title": "Inception",
                "year": 2010,
                "ids": {"trakt": "1"},
                "overview": "A thief who steals corporate secrets through the use of dream-sharing technology.",
            },
        },
        {
            "watchers": 120,
            "movie": {
                "title": "The Dark Knight",
                "year": 2008,
                "ids": {"trakt": "2"},
                "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham.",
            },
        },
    ]
