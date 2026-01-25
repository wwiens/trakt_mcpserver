import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from config.api import DEFAULT_MAX_PAGES
from server.comments.tools import fetch_movie_comments
from server.movies.tools import (
    fetch_movie_ratings,
    fetch_movie_summary,
    fetch_movie_videos,
    fetch_related_movies,
    fetch_trending_movies,
)
from utils.api.error_types import (
    TraktResourceNotFoundError,
)
from utils.api.errors import InternalError


@pytest.mark.asyncio
async def test_fetch_trending_movies():
    sample_movies = [
        {
            "watchers": 150,
            "movie": {
                "title": "Inception",
                "year": 2010,
                "overview": "A thief who steals corporate secrets through dream-sharing technology.",
            },
        }
    ]

    with patch("server.movies.tools.TrendingMoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_movies)
        mock_client.get_trending_movies.return_value = future

        result = await fetch_trending_movies(limit=5)

        assert "# Trending Movies on Trakt" in result
        assert "Inception (2010)" in result
        assert "150 watchers" in result

        mock_client.get_trending_movies.assert_called_once_with(limit=5, page=None)


@pytest.mark.asyncio
async def test_fetch_movie_comments():
    sample_comments = [
        {
            "user": {"username": "user1"},
            "created_at": "2023-01-15T20:30:00Z",
            "comment": "This is a great movie!",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 10,
            "id": "123",
        }
    ]

    with patch("server.comments.tools.MovieCommentsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_result(sample_comments)
        mock_client.get_movie_comments.return_value = comments_future

        result = await fetch_movie_comments(movie_id="1", limit=5)

        assert "# Comments for Movie ID: 1" in result
        assert "user1" in result
        assert "This is a great movie!" in result

        mock_client.get_movie_comments.assert_called_once_with(
            "1", limit=5, sort="newest", page=None, max_pages=DEFAULT_MAX_PAGES
        )


@pytest.mark.asyncio
async def test_fetch_movie_ratings():
    sample_movie = {"title": "Inception", "year": 2010}

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
            "1": 2,
        },
    }

    with patch("server.movies.tools.MovieDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        movie_future: asyncio.Future[Any] = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future

        ratings_future: asyncio.Future[Any] = asyncio.Future()
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
    with patch("server.movies.tools.MovieDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie.return_value = future

        with pytest.raises(InternalError) as exc_info:
            await fetch_movie_ratings(movie_id="1")

        # The function should raise an InternalError for unexpected exceptions
        assert "An unexpected error occurred" in str(exc_info.value)

        mock_client.get_movie.assert_called_once_with("1")
        mock_client.get_movie_ratings.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_movie_comments_string_error_handling():
    """Test fetching movie comments with a string error response."""
    with patch("server.comments.tools.MovieCommentsClient") as mock_client_class:
        # Configure the mock to return a string error
        mock_client = mock_client_class.return_value

        # Create a future that returns a string error
        comments_future: asyncio.Future[Any] = asyncio.Future()
        comments_future.set_exception(
            TraktResourceNotFoundError(
                "movie", "1", "The requested movie was not found."
            )
        )
        mock_client.get_movie_comments.return_value = comments_future

        # Verify the result contains the error message
        with pytest.raises(TraktResourceNotFoundError):
            await fetch_movie_comments(movie_id="1", limit=5)

        # Verify the client methods were called
        mock_client.get_movie_comments.assert_called_once_with(
            "1", limit=5, sort="newest", page=None, max_pages=DEFAULT_MAX_PAGES
        )


@pytest.mark.asyncio
async def test_fetch_movie_summary_extended():
    """Test fetching movie summary with extended data (default)."""
    sample_movie = {
        "title": "The Matrix",
        "year": 1999,
        "ids": {"trakt": 12345},
        "tagline": "The future is not set.",
        "overview": "A computer hacker learns about the true nature of reality.",
        "released": "1999-03-31",
        "runtime": 136,
        "country": "us",
        "status": "released",
        "rating": 8.7,
        "votes": 150,
        "comment_count": 75,
        "languages": ["en"],
        "genres": ["action", "sci-fi"],
        "certification": "R",
        "homepage": "http://www.thematrix.com/",
    }

    with patch("server.movies.tools.MovieDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        movie_future: asyncio.Future[Any] = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie_extended.return_value = movie_future

        result = await fetch_movie_summary(movie_id="12345")

        assert "## The Matrix (1999) - Released" in result
        assert "*The future is not set.*" in result
        assert "A computer hacker learns about the true nature of reality." in result
        assert "- Status: released" in result
        assert "- Runtime: 136 minutes" in result
        assert "- Certification: R" in result
        assert "- Released: 1999-03-31" in result
        assert "- Country: US" in result
        assert "- Genres: action, sci-fi" in result
        assert "- Languages: en" in result
        assert "- Homepage: http://www.thematrix.com/" in result
        assert "- Rating: 8.7/10 (150 votes)" in result
        assert "- Comments: 75" in result
        assert "Trakt ID: 12345" in result

        mock_client.get_movie_extended.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_basic():
    """Test fetching movie summary with basic data only."""
    sample_movie = {
        "title": "The Matrix",
        "year": 1999,
        "ids": {"trakt": 12345},
    }

    with patch("server.movies.tools.MovieDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        movie_future: asyncio.Future[Any] = asyncio.Future()
        movie_future.set_result(sample_movie)
        mock_client.get_movie.return_value = movie_future

        result = await fetch_movie_summary(movie_id="12345", extended=False)

        assert "## The Matrix (1999)" in result
        assert "Trakt ID: 12345" in result
        # Should not contain extended data
        assert "- Status:" not in result
        assert "- Runtime:" not in result
        assert "- Certification:" not in result

        mock_client.get_movie.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_extended_error():
    """Test fetching movie summary with extended mode error."""
    with patch("server.movies.tools.MovieDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie_extended.return_value = future

        with pytest.raises(InternalError) as exc_info:
            await fetch_movie_summary(movie_id="12345")

        # The function should raise an InternalError for unexpected exceptions
        assert "An unexpected error occurred" in str(exc_info.value)
        mock_client.get_movie_extended.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_basic_error():
    """Test fetching movie summary with basic mode error."""
    with patch("server.movies.tools.MovieDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("API error"))
        mock_client.get_movie.return_value = future

        with pytest.raises(InternalError) as exc_info:
            await fetch_movie_summary(movie_id="12345", extended=False)

        # The function should raise an InternalError for unexpected exceptions
        assert "An unexpected error occurred" in str(exc_info.value)
        mock_client.get_movie.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_extended_string_error():
    """Test fetching movie summary with extended mode string error response."""
    with patch("server.movies.tools.MovieDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("Error: Movie not found")
        mock_client.get_movie_extended.return_value = future

        # handle_api_string_error returns InternalError for string errors
        with pytest.raises(Exception) as exc_info:
            await fetch_movie_summary(movie_id="12345")

        # Check that it's an InternalError with the right message
        assert "Error accessing movie_extended" in str(
            exc_info.value
        ) or "An unexpected error occurred" in str(exc_info.value)

        mock_client.get_movie_extended.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_summary_basic_string_error():
    """Test fetching movie summary with basic mode string error response."""
    with patch("server.movies.tools.MovieDetailsClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("Error: Movie not found")
        mock_client.get_movie.return_value = future

        # handle_api_string_error returns InternalError for string errors
        with pytest.raises(Exception) as exc_info:
            await fetch_movie_summary(movie_id="12345", extended=False)

        # Check that it's an InternalError with the right message
        assert "Error accessing movie" in str(
            exc_info.value
        ) or "An unexpected error occurred" in str(exc_info.value)

        mock_client.get_movie.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_fetch_movie_videos_with_embeds():
    """Test fetching movie videos with iframe embeds."""
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        # Mock video data
        mock_videos = [
            {
                "title": "Official Trailer",
                "url": "https://youtube.com/watch?v=ABC123DEF12",
                "site": "youtube",
                "type": "trailer",
                "size": 1080,
                "official": True,
                "published_at": "2025-06-05T00:00:00.000Z",
                "country": "us",
                "language": "en",
            }
        ]

        mock_movie = {"title": "Test Movie", "year": 2025}

        mock_client.get_videos = AsyncMock(return_value=mock_videos)
        mock_client.get_movie = AsyncMock(return_value=mock_movie)

        result = await fetch_movie_videos("test-movie", embed_markdown=True)

        # Verify result content
        assert "# Videos for Test Movie" in result
        assert (
            "**ALWAYS:** Preserve iframe HTML below exactly as provided so videos embed and display properly in the response"
            in result
        )
        assert "<iframe" in result
        assert "https://www.youtube.com/embed/ABC123DEF12" in result


@pytest.mark.asyncio
async def test_fetch_movie_videos_without_embeds():
    """Test fetching movie videos without iframe embeds."""
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_videos = [
            {
                "title": "Official Trailer",
                "url": "https://youtube.com/watch?v=ABC123DEF12",
                "site": "youtube",
                "type": "trailer",
            }
        ]

        mock_movie = {"title": "Test Movie"}

        mock_client.get_videos = AsyncMock(return_value=mock_videos)
        mock_client.get_movie = AsyncMock(return_value=mock_movie)

        result = await fetch_movie_videos("test-movie", embed_markdown=False)

        # Should not contain iframe or instructional text
        assert (
            "**ALWAYS:** Preserve iframe HTML below exactly as provided so videos embed and display properly in the response"
            not in result
        )
        assert "<iframe" not in result
        assert "[▶️ Watch on YouTube]" in result


@pytest.mark.asyncio
async def test_fetch_movie_videos_no_videos():
    """Test movie video fetching with no videos available."""
    with patch("server.movies.tools.MoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        mock_client.get_videos = AsyncMock(return_value=[])  # No videos

        mock_movie = {"title": "Test Movie"}

        mock_client.get_movie = AsyncMock(return_value=mock_movie)

        result = await fetch_movie_videos("test-movie", embed_markdown=True)

        # Should handle empty video list gracefully
        assert "# Videos for Test Movie" in result
        assert "No videos available." in result


@pytest.mark.asyncio
async def test_fetch_related_movies():
    """Test fetching related movies."""
    sample_movies = [
        {
            "title": "The Dark Knight Rises",
            "year": 2012,
            "overview": "Eight years after the Joker's reign of anarchy.",
            "ids": {"trakt": 28, "slug": "the-dark-knight-rises"},
        },
        {
            "title": "Batman Begins",
            "year": 2005,
            "overview": "A young Bruce Wayne travels to the Far East.",
            "ids": {"trakt": 155, "slug": "batman-begins"},
        },
    ]

    with patch("server.movies.tools.RelatedMoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_related_movies = AsyncMock(return_value=sample_movies)

        result = await fetch_related_movies(movie_id="the-dark-knight", limit=10)

        assert "# Related Movies" in result
        assert "The Dark Knight Rises (2012)" in result
        assert "Batman Begins (2005)" in result
        assert "Eight years after the Joker's reign of anarchy." in result

        mock_client.get_related_movies.assert_called_once_with(
            movie_id="the-dark-knight", limit=10, page=None
        )


@pytest.mark.asyncio
async def test_fetch_related_movies_empty():
    """Test fetching related movies with no results."""
    with patch("server.movies.tools.RelatedMoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_related_movies = AsyncMock(return_value=[])

        result = await fetch_related_movies(movie_id="obscure-movie", limit=10)

        assert "# Related Movies" in result
        assert "No related movies found." in result

        mock_client.get_related_movies.assert_called_once_with(
            movie_id="obscure-movie", limit=10, page=None
        )


@pytest.mark.asyncio
async def test_fetch_related_movies_with_page():
    """Test fetching related movies with pagination."""
    from models.types.pagination import PaginatedResponse, PaginationMetadata

    sample_movies = [
        {
            "title": "The Dark Knight Rises",
            "year": 2012,
            "ids": {"trakt": 28, "slug": "the-dark-knight-rises"},
        }
    ]

    paginated_response = PaginatedResponse(
        data=sample_movies,
        pagination=PaginationMetadata(
            current_page=2,
            items_per_page=10,
            total_pages=3,
            total_items=25,
        ),
    )

    with patch("server.movies.tools.RelatedMoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_related_movies = AsyncMock(return_value=paginated_response)

        result = await fetch_related_movies(
            movie_id="the-dark-knight", limit=10, page=2
        )

        assert "# Related Movies" in result
        assert "The Dark Knight Rises (2012)" in result
        # Assert specific pagination output from format_pagination_header
        assert "Page 2 of 3" in result
        assert "of 25" in result  # Total items shown as "items X-Y of 25"
        # Navigation hints should appear since page 2 has both previous and next
        assert "Previous: page 1" in result
        assert "Next: page 3" in result

        mock_client.get_related_movies.assert_called_once_with(
            movie_id="the-dark-knight", limit=10, page=2
        )


@pytest.mark.asyncio
async def test_fetch_related_movies_error():
    """Test fetching related movies with error."""
    with patch("server.movies.tools.RelatedMoviesClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_related_movies = AsyncMock(side_effect=Exception("API error"))

        with pytest.raises(InternalError):
            await fetch_related_movies(movie_id="the-dark-knight", limit=10)
