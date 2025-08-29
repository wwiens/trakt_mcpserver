import os
import sys
import time
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from client.sync.client import SyncClient

# Add project root to path - more explicit approach
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also add project root using pathlib as backup
project_root_pathlib = str(Path(__file__).parent.parent.resolve())
if project_root_pathlib not in sys.path:
    sys.path.insert(0, project_root_pathlib)


@pytest.fixture
def mock_auth_token():
    """Create a mock auth token for testing."""
    from models.auth import TraktAuthToken

    return TraktAuthToken(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )


@pytest.fixture
def authenticated_sync_client() -> Generator["SyncClient", None, None]:
    """Create an authenticated sync client for testing."""
    from client.sync.client import SyncClient
    from models.auth.auth import TraktAuthToken

    # Consolidate token construction into a single variable
    mock_auth_token = TraktAuthToken(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=7200,
        created_at=int(time.time()),
        scope="public",
        token_type="bearer",
    )

    client = SyncClient()
    client.auth_token = mock_auth_token

    yield client

    # Cleanup: check for and call client.close() if it exists
    if hasattr(client, "close"):
        close_method = getattr(client, "close", None)
        if close_method and callable(close_method):
            try:
                result = close_method()
                # Check if result is awaitable (for async methods)
                if hasattr(result, "__await__"):
                    import asyncio

                    try:
                        asyncio.get_event_loop().run_until_complete(result)  # type: ignore[arg-type]
                    except RuntimeError:
                        # No event loop running, create a new one
                        asyncio.run(result)  # type: ignore[arg-type]
            except Exception:
                # Ignore cleanup errors to avoid breaking tests - client may not have close()
                # or cleanup may fail, but we don't want this to break test execution
                return


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
