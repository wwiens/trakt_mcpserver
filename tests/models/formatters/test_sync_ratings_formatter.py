"""Tests for sync ratings formatters."""

from __future__ import annotations

from datetime import datetime

from models.formatters.sync_ratings import SyncRatingsFormatters
from models.movies.movie import TraktMovie
from models.shows.episode import TraktEpisode
from models.shows.show import TraktShow
from models.sync.ratings import TraktSeason, TraktSyncRating
from models.types.pagination import PaginatedResponse, PaginationMetadata


class TestSyncRatingsFormatters:
    """Test cases for SyncRatingsFormatters."""

    def test_format_user_ratings_episode_formatting(self) -> None:
        """Test that episode ratings use proper SxxExx formatting."""
        # Create test episode rating data
        episode_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=9,
            type="episode",
            episode=TraktEpisode(
                season=2,
                number=5,
                title="Dead Freight",
                ids={
                    "trakt": "123",
                    "tvdb": "456",
                    "imdb": "tt789",
                    "tmdb": "101112",
                },
            ),
            show=TraktShow(
                title="Breaking Bad",
                year=2008,
                ids={
                    "trakt": "1",
                    "slug": "breaking-bad",
                    "tvdb": "81189",
                    "imdb": "tt0903747",
                    "tmdb": "1396",
                },
            ),
        )

        paginated_response = PaginatedResponse(
            data=[episode_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=1, total_pages=1, total_items=1
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="episodes"
        )

        # Verify SxxExx formatting is used
        assert "Breaking Bad - S02E05: Dead Freight (2008)" in result
        assert "Rating 9/10" in result

    def test_format_user_ratings_episode_without_title(self) -> None:
        """Test episode formatting when episode has no title."""
        episode_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=7,
            type="episode",
            episode=TraktEpisode(
                season=1,
                number=3,
                title=None,  # No title
                ids={"trakt": "123"},
            ),
            show=TraktShow(
                title="Test Show",
                year=2020,
                ids={"trakt": "1"},
            ),
        )

        paginated_response = PaginatedResponse(
            data=[episode_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=1, total_pages=1, total_items=1
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="episodes"
        )

        # Verify SxxExx formatting without title
        assert "Test Show - S01E03 (2020)" in result
        assert "Rating 7/10" in result

    def test_format_user_ratings_season_formatting(self) -> None:
        """Test that season ratings use proper 'Season N' formatting."""
        season_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=8,
            type="season",
            season=TraktSeason(number=3, ids={"trakt": "456", "tvdb": "789"}),
            show=TraktShow(
                title="Game of Thrones",
                year=2011,
                ids={"trakt": "1", "slug": "game-of-thrones"},
            ),
        )

        paginated_response = PaginatedResponse(
            data=[season_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=1, total_pages=1, total_items=1
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="seasons"
        )

        # Verify Season N formatting is used
        assert "Game of Thrones - Season 3 (2011)" in result
        assert "Rating 8/10" in result

    def test_format_user_ratings_show_formatting(self) -> None:
        """Test that generic show ratings use proper show formatting."""
        show_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=10,
            type="show",
            show=TraktShow(
                title="The Wire",
                year=2002,
                ids={"trakt": "1", "slug": "the-wire"},
            ),
        )

        paginated_response = PaginatedResponse(
            data=[show_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=1, total_pages=1, total_items=1
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="shows"
        )

        # Verify show formatting
        assert "The Wire (2002)" in result
        assert "Rating 10/10" in result

    def test_format_user_ratings_movie_formatting(self) -> None:
        """Test that movie ratings use proper movie formatting."""
        movie_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=9,
            type="movie",
            movie=TraktMovie(
                title="Inception",
                year=2010,
                ids={"trakt": "1", "slug": "inception-2010", "imdb": "tt1375666"},
            ),
        )

        paginated_response = PaginatedResponse(
            data=[movie_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=1, total_pages=1, total_items=1
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="movies"
        )

        # Verify movie formatting
        assert "Inception (2010)" in result
        assert "Rating 9/10" in result

    def test_format_user_ratings_mixed_types_order(self) -> None:
        """Test that when mixed types have show data, specific formatting is used."""
        # Create episode, season, and show ratings that all have show data
        episode_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=8,
            type="episode",
            episode=TraktEpisode(
                season=1,
                number=1,
                title="Pilot",
                ids={"trakt": "1"},
            ),
            show=TraktShow(
                title="Test Show",
                year=2020,
                ids={"trakt": "1"},
            ),
        )

        season_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=8,
            type="season",
            season=TraktSeason(number=1, ids={"trakt": "1"}),
            show=TraktShow(
                title="Test Show",
                year=2020,
                ids={"trakt": "1"},
            ),
        )

        show_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=8,
            type="show",
            show=TraktShow(
                title="Test Show",
                year=2020,
                ids={"trakt": "1"},
            ),
        )

        paginated_response = PaginatedResponse(
            data=[episode_rating, season_rating, show_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=3, total_pages=1, total_items=3
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="mixed"
        )

        # Verify each type uses its specific formatting despite all having show data
        assert "Test Show - S01E01: Pilot (2020)" in result  # Episode-specific
        assert "Test Show - Season 1 (2020)" in result  # Season-specific
        assert "Test Show (2020)" in result  # Show-specific
        assert "Rating 8/10 (3 mixed)" in result

    def test_format_user_ratings_with_zero_year(self) -> None:
        """Test formatting when years are zero (edge case)."""
        episode_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=6,
            type="episode",
            episode=TraktEpisode(
                season=1,
                number=1,
                title="Episode One",
                ids={"trakt": "1"},
            ),
            show=TraktShow(
                title="Zero Year Show",
                year=0,
                ids={"trakt": "1"},
            ),
        )

        paginated_response = PaginatedResponse(
            data=[episode_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=1, total_pages=1, total_items=1
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="episodes"
        )

        # Verify formatting without year when year is 0 (falsy)
        assert "Zero Year Show - S01E01: Episode One" in result
        assert (
            "Zero Year Show - S01E01: Episode One (" not in result
        )  # No year parentheses

    def test_format_user_ratings_edge_case_double_digit_episode(self) -> None:
        """Test SxxExx formatting with double-digit season and episode numbers."""
        episode_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=10,
            type="episode",
            episode=TraktEpisode(
                season=12,
                number=34,
                title="Big Numbers",
                ids={"trakt": "1"},
            ),
            show=TraktShow(
                title="Long Running Show",
                year=1990,
                ids={"trakt": "1"},
            ),
        )

        paginated_response = PaginatedResponse(
            data=[episode_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=1, total_pages=1, total_items=1
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="episodes"
        )

        # Verify proper zero-padding for SxxExx format
        assert "Long Running Show - S12E34: Big Numbers (1990)" in result

    def test_format_user_ratings_edge_case_single_digit_episode(self) -> None:
        """Test SxxExx formatting with single-digit season and episode numbers (zero-padded)."""
        episode_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2024-01-01T10:00:00.000+00:00"),
            rating=5,
            type="episode",
            episode=TraktEpisode(
                season=1,
                number=9,
                title="Single Digit",
                ids={"trakt": "1"},
            ),
            show=TraktShow(
                title="New Show",
                year=2024,
                ids={"trakt": "1"},
            ),
        )

        paginated_response = PaginatedResponse(
            data=[episode_rating],
            pagination=PaginationMetadata(
                current_page=1, items_per_page=1, total_pages=1, total_items=1
            ),
        )

        result = SyncRatingsFormatters.format_user_ratings(
            paginated_response, rating_type="episodes"
        )

        # Verify proper zero-padding for single digits
        assert "New Show - S01E09: Single Digit (2024)" in result
