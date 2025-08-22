import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.comments.tools import (
    fetch_episode_comments,
    fetch_season_comments,
    fetch_show_comments,
)
from server.shows.tools import (
    fetch_favorited_shows,
    fetch_played_shows,
    fetch_popular_shows,
    fetch_show_ratings,
    fetch_show_summary,
    fetch_show_videos,
    fetch_trending_shows,
    fetch_watched_shows,
)
from utils.api.error_types import (
    TraktResourceNotFoundError,
)
from utils.api.errors import InternalError


@pytest.mark.asyncio
async def test_fetch_trending_shows():
    sample_shows = [
        {
            "watchers": 100,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            },
        }
    ]

    with patch("server.shows.tools.TrendingShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_trending_shows = AsyncMock(return_value=sample_shows)

        result = await fetch_trending_shows(limit=5)

        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result

        mock_client.get_trending_shows.assert_called_once_with(limit=5)


@pytest.mark.asyncio
async def test_fetch_popular_shows():
    sample_shows = [
        {
            "title": "Breaking Bad",
            "year": 2008,
            "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
        }
    ]

    with patch("server.shows.tools.PopularShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_popular_shows = AsyncMock(return_value=sample_shows)

        result = await fetch_popular_shows(limit=5)

        assert "# Popular Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        mock_client.get_popular_shows.assert_called_once()
        _, kwargs = mock_client.get_popular_shows.call_args
        assert kwargs.get("limit") == 5


@pytest.mark.asyncio
async def test_fetch_favorited_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.tools.ShowStatsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_favorited_shows = AsyncMock(return_value=sample_shows)

        result = await fetch_favorited_shows(limit=5, period="weekly")

        assert "# Most Favorited Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        mock_client.get_favorited_shows.assert_called_once_with(
            limit=5, period="weekly"
        )


@pytest.mark.asyncio
async def test_fetch_played_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.tools.ShowStatsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_played_shows = AsyncMock(return_value=sample_shows)

        result = await fetch_played_shows(limit=5, period="weekly")

        assert "# Most Played Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        mock_client.get_played_shows.assert_called_once_with(limit=5, period="weekly")


@pytest.mark.asyncio
async def test_fetch_watched_shows():
    sample_shows = [
        {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
            }
        }
    ]

    with patch("server.shows.tools.ShowStatsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_watched_shows = AsyncMock(return_value=sample_shows)

        result = await fetch_watched_shows(limit=5, period="weekly")

        assert "# Most Watched Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result

        mock_client.get_watched_shows.assert_called_once_with(limit=5, period="weekly")


@pytest.mark.asyncio
async def test_fetch_show_comments():
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This is a great show!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123",
        }
    ]

    with (
        patch("server.comments.tools.ShowCommentsClient") as mock_comments_client_class,
    ):
        mock_client = mock_comments_client_class.return_value
        mock_client.get_show_comments = AsyncMock(return_value=sample_comments)

        result = await fetch_show_comments(show_id="1", limit=5)

        assert "# Comments for Show ID: 1" in result
        assert "user1" in result
        assert "This is a great show!" in result

        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_show_ratings():
    sample_show = {"title": "Breaking Bad", "year": 2008}

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
            "1": 1,
        },
    }

    with patch("server.shows.tools.ShowDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_show = AsyncMock(return_value=sample_show)
        mock_client.get_show_ratings = AsyncMock(return_value=sample_ratings)

        result = await fetch_show_ratings(show_id="1")

        assert "# Ratings for Breaking Bad" in result
        assert "**Average Rating:** 9.00/10" in result
        assert "from 1000 votes" in result

        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_fetch_show_ratings_error():
    with patch("server.shows.tools.ShowDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_show = AsyncMock(side_effect=Exception("API error"))

        with pytest.raises(InternalError):
            await fetch_show_ratings(show_id="1")

        mock_client.get_show.assert_called_once_with("1")
        mock_client.get_show_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_show_comments_not_found_propagation():
    """Test fetching show comments with TraktResourceNotFoundError propagation."""
    with (
        patch("server.comments.tools.ShowCommentsClient") as mock_comments_client_class,
    ):
        # Configure the mock to raise a TraktResourceNotFoundError
        mock_client = mock_comments_client_class.return_value
        mock_client.get_show_comments = AsyncMock(
            side_effect=TraktResourceNotFoundError(
                "show", "1", "The requested show was not found."
            )
        )

        # Verify the result contains the error message
        with pytest.raises(TraktResourceNotFoundError):
            await fetch_show_comments(show_id="1", limit=5)

        # Verify the client methods were called
        mock_client.get_show_comments.assert_called_once_with(
            "1", limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_season_comments_not_found_propagation():
    """Test fetching season comments with TraktResourceNotFoundError propagation."""
    with (
        patch(
            "server.comments.tools.SeasonCommentsClient"
        ) as mock_comments_client_class,
    ):
        # Configure the mock to raise a TraktResourceNotFoundError
        mock_client = mock_comments_client_class.return_value
        mock_client.get_season_comments = AsyncMock(
            side_effect=TraktResourceNotFoundError(
                "show", "1", "The requested show was not found."
            )
        )

        # Verify the result contains the error message
        with pytest.raises(TraktResourceNotFoundError):
            await fetch_season_comments(show_id="1", season=1, limit=5)

        # Verify the client methods were called
        mock_client.get_season_comments.assert_called_once_with(
            "1", 1, limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_episode_comments_not_found_propagation():
    """Test fetching episode comments with TraktResourceNotFoundError propagation."""
    with (
        patch(
            "server.comments.tools.EpisodeCommentsClient"
        ) as mock_comments_client_class,
    ):
        # Configure the mock to raise a TraktResourceNotFoundError
        mock_client = mock_comments_client_class.return_value
        mock_client.get_episode_comments = AsyncMock(
            side_effect=TraktResourceNotFoundError(
                "show", "1", "The requested show was not found."
            )
        )

        # With proper MCP error propagation, we expect an exception
        with pytest.raises(TraktResourceNotFoundError) as exc_info:
            await fetch_episode_comments(show_id="1", season=1, episode=1, limit=5)

        assert exc_info.value.data is not None
        assert exc_info.value.data["resource_type"] == "show"
        assert exc_info.value.data["resource_id"] == "1"
        assert "The requested show was not found" in str(exc_info.value)

        # Verify the client methods were called
        mock_client.get_episode_comments.assert_called_once_with(
            "1", 1, 1, limit=5, sort="newest"
        )


@pytest.mark.asyncio
async def test_fetch_show_summary_extended():
    """Test fetching show summary with extended data (default)."""
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008,
        "ids": {"trakt": 54321},
        "tagline": "Chemistry is the study of change.",
        "overview": "A high school chemistry teacher turned meth producer.",
        "first_aired": "2008-01-20T02:00:00.000Z",
        "airs": {"day": "Sunday", "time": "21:00", "timezone": "America/New_York"},
        "runtime": 47,
        "certification": "TV-MA",
        "network": "AMC",
        "country": "us",
        "status": "ended",
        "rating": 9.5,
        "votes": 200,
        "comment_count": 150,
        "languages": ["en"],
        "genres": ["drama", "crime"],
        "aired_episodes": 62,
        "homepage": "http://www.amc.com/shows/breaking-bad",
    }

    with patch("server.shows.tools.ShowDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_show_extended = AsyncMock(return_value=sample_show)

        result = await fetch_show_summary(show_id="54321")

        assert "## Breaking Bad (2008) - Ended" in result
        assert "*Chemistry is the study of change.*" in result
        assert "A high school chemistry teacher turned meth producer." in result
        assert "- Status: ended" in result
        assert "- Runtime: 47 minutes" in result
        assert "- Certification: TV-MA" in result
        assert "- Network: AMC" in result
        assert "- Air Time: Sundays at 21:00 (America/New_York)" in result
        assert "- Aired Episodes: 62" in result
        assert "- Country: US" in result
        assert "- Genres: drama, crime" in result
        assert "- Languages: en" in result
        assert "- Homepage: http://www.amc.com/shows/breaking-bad" in result
        assert "- Rating: 9.5/10 (200 votes)" in result
        assert "- Comments: 150" in result
        assert "Trakt ID: 54321" in result

        mock_client.get_show_extended.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_basic():
    """Test fetching show summary with basic data only."""
    sample_show = {
        "title": "Breaking Bad",
        "year": 2008,
        "ids": {"trakt": 54321},
    }

    with patch("server.shows.tools.ShowDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_show = AsyncMock(return_value=sample_show)

        result = await fetch_show_summary(show_id="54321", extended=False)

        assert "## Breaking Bad (2008)" in result
        assert "Trakt ID: 54321" in result
        # Should not contain extended data
        assert "- Status:" not in result
        assert "- Runtime:" not in result
        assert "- Network:" not in result
        assert "- Air Time:" not in result

        mock_client.get_show.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_extended_error():
    """Test fetching show summary with extended mode error."""
    with patch("server.shows.tools.ShowDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_show_extended = AsyncMock(side_effect=Exception("API error"))

        with pytest.raises(InternalError) as exc_info:
            await fetch_show_summary(show_id="54321")

        # The function should raise an InternalError for unexpected exceptions
        assert "An unexpected error occurred" in str(exc_info.value)
        mock_client.get_show_extended.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_basic_error():
    """Test fetching show summary with basic mode error."""
    with patch("server.shows.tools.ShowDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_show = AsyncMock(side_effect=Exception("API error"))

        with pytest.raises(InternalError) as exc_info:
            await fetch_show_summary(show_id="54321", extended=False)

        # The function should raise an InternalError for unexpected exceptions
        assert "An unexpected error occurred" in str(exc_info.value)
        mock_client.get_show.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_extended_string_error():
    """Test fetching show summary with extended mode string error response."""
    with patch("server.shows.tools.ShowDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_client.get_show_extended = AsyncMock(return_value="Error: Show not found")

        # handle_api_string_error returns InternalError for string errors
        with pytest.raises(InternalError):
            await fetch_show_summary(show_id="54321")

        mock_client.get_show_extended.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_summary_basic_string_error():
    """Test fetching show summary with basic mode string error response."""
    with patch("server.shows.tools.ShowDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_show = AsyncMock(return_value="Error: Show not found")

        # handle_api_string_error returns InternalError for string errors
        with pytest.raises(InternalError) as exc_info:
            await fetch_show_summary(show_id="54321", extended=False)

        # Check that it's an InternalError with the right message
        assert "Error accessing show" in str(
            exc_info.value
        ) or "An unexpected error occurred" in str(exc_info.value)

        mock_client.get_show.assert_called_once_with("54321")


@pytest.mark.asyncio
async def test_fetch_show_videos_with_embeds():
    """Test fetching show videos with iframe embeds."""
    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock video data
        mock_videos = [
            {
                "title": "Official Trailer",
                "url": "https://youtube.com/watch?v=ZbsiKjVAV28",
                "site": "youtube",
                "type": "trailer",
                "size": 1080,
                "official": True,
                "published_at": "2025-06-05T00:00:00.000Z",
                "country": "us",
                "language": "en",
            }
        ]

        mock_show = {"title": "Test Show", "year": 2025}

        mock_client.get_videos = AsyncMock(return_value=mock_videos)
        mock_client.get_show = AsyncMock(return_value=mock_show)

        result = await fetch_show_videos("test-show", embed_markdown=True)

        # Verify client calls
        mock_client.get_videos.assert_called_once_with("test-show")
        mock_client.get_show.assert_called_once_with("test-show")

        # Verify result content
        assert "# Videos for Test Show" in result
        assert "PRESERVE THIS IFRAME HTML" in result
        assert "<iframe" in result
        assert "https://www.youtube.com/embed/ZbsiKjVAV28" in result


@pytest.mark.asyncio
async def test_fetch_show_videos_without_embeds():
    """Test fetching show videos without iframe embeds."""
    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_videos = [
            {
                "title": "Official Trailer",
                "url": "https://youtube.com/watch?v=ZbsiKjVAV28",
                "site": "youtube",
                "type": "trailer",
            }
        ]

        mock_show = {"title": "Test Show"}

        mock_client.get_videos = AsyncMock(return_value=mock_videos)
        mock_client.get_show = AsyncMock(return_value=mock_show)

        result = await fetch_show_videos("test-show", embed_markdown=False)

        # Should not contain iframe or instructional text
        assert "PRESERVE THIS IFRAME HTML" not in result
        assert "<iframe" not in result
        assert "[▶️ Watch on Youtube]" in result


@pytest.mark.asyncio
async def test_fetch_show_videos_show_fetch_failure():
    """Test show video fetching when show details fetch fails."""
    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_videos = [
            {
                "title": "Official Trailer",
                "url": "https://youtube.com/watch?v=ZbsiKjVAV28",
                "site": "youtube",
                "type": "trailer",
            }
        ]

        mock_client.get_videos = AsyncMock(return_value=mock_videos)
        mock_client.get_show = AsyncMock(side_effect=InternalError("Show not found"))

        result = await fetch_show_videos("test-show", embed_markdown=True)

        # Should use fallback title
        assert "Show ID: test-show" in result
        assert "<iframe" in result  # Videos should still be processed


@pytest.mark.asyncio
async def test_fetch_show_videos_string_error_handling():
    """Test show video fetching with string error responses."""
    with patch("server.shows.tools.ShowsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_videos = [
            {
                "title": "Official Trailer",
                "url": "https://youtube.com/watch?v=ZbsiKjVAV28",
                "site": "youtube",
                "type": "trailer",
            }
        ]

        mock_client.get_videos = AsyncMock(return_value=mock_videos)
        mock_client.get_show = AsyncMock(return_value="Show not found")

        # Should handle string error gracefully and use fallback title
        result = await fetch_show_videos("test-show", embed_markdown=True)

        # Should use fallback title since string error triggers fallback behavior
        assert "Show ID: test-show" in result
        assert "<iframe" in result  # Videos should still be processed
