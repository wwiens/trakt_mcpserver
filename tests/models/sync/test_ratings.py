"""Tests for the models.sync.ratings module."""

from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from models.sync.ratings import (
    SyncRatingsNotFound,
    SyncRatingsSummary,
    SyncRatingsSummaryCount,
    TraktSeason,
    TraktSyncRating,
    TraktSyncRatingItem,
    TraktSyncRatingsRequest,
)

if TYPE_CHECKING:
    from tests.models.test_data_types import SyncRatingItemTestData, SyncRatingTestData


class TestTraktSeason:
    """Tests for the TraktSeason model."""

    def test_valid_season_creation(self):
        """Test creating a valid TraktSeason instance."""
        season = TraktSeason(
            number=1, ids={"trakt": "140912", "tvdb": "703353", "tmdb": "81266"}
        )

        assert season.number == 1
        assert season.ids is not None
        assert season.ids["trakt"] == "140912"
        assert season.ids["tvdb"] == "703353"
        assert season.ids["tmdb"] == "81266"

    def test_season_without_ids(self):
        """Test creating season without IDs."""
        season = TraktSeason(number=2)
        assert season.number == 2
        assert season.ids is None


class TestTraktSyncRating:
    """Tests for the TraktSyncRating model."""

    def test_valid_movie_rating_creation(self):
        """Test creating a valid movie rating from API response data."""
        rating_data: SyncRatingTestData = {
            "rated_at": "2014-09-01T09:10:11.000Z",
            "rating": 10,
            "type": "movie",
            "movie": {
                "title": "TRON: Legacy",
                "year": 2010,
                "ids": {
                    "trakt": "1",
                    "slug": "tron-legacy-2010",
                    "imdb": "tt1104001",
                    "tmdb": "20526",
                },
            },
        }

        rating = TraktSyncRating.model_validate(rating_data)

        assert rating.rated_at == "2014-09-01T09:10:11.000Z"
        assert rating.rating == 10
        assert rating.type == "movie"
        assert rating.movie is not None
        assert rating.movie.title == "TRON: Legacy"
        assert rating.movie.year == 2010
        assert rating.show is None
        assert rating.season is None
        assert rating.episode is None

    def test_valid_show_rating_creation(self):
        """Test creating a valid show rating from API response data."""
        rating_data: SyncRatingTestData = {
            "rated_at": "2014-09-01T09:10:11.000Z",
            "rating": 10,
            "type": "show",
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {
                    "trakt": "1",
                    "slug": "breaking-bad",
                    "tvdb": "81189",
                    "imdb": "tt0903747",
                    "tmdb": "1396",
                },
            },
        }

        rating = TraktSyncRating.model_validate(rating_data)

        assert rating.rated_at == "2014-09-01T09:10:11.000Z"
        assert rating.rating == 10
        assert rating.type == "show"
        assert rating.show is not None
        assert rating.show.title == "Breaking Bad"
        assert rating.show.year == 2008
        assert rating.movie is None

    def test_valid_season_rating_creation(self):
        """Test creating a valid season rating from API response data."""
        rating_data: SyncRatingTestData = {
            "rated_at": "2014-09-01T09:10:11.000Z",
            "rating": 8,
            "type": "season",
            "season": {"number": 1, "ids": {"tvdb": "30272", "tmdb": "3572"}},
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {
                    "trakt": "1",
                    "slug": "breaking-bad",
                    "tvdb": "81189",
                    "imdb": "tt0903747",
                    "tmdb": "1396",
                },
            },
        }

        rating = TraktSyncRating.model_validate(rating_data)

        assert rating.rated_at == "2014-09-01T09:10:11.000Z"
        assert rating.rating == 8
        assert rating.type == "season"
        assert rating.season is not None
        assert rating.season.number == 1
        assert rating.show is not None
        assert rating.show.title == "Breaking Bad"

    def test_valid_episode_rating_creation(self):
        """Test creating a valid episode rating from API response data."""
        rating_data: SyncRatingTestData = {
            "rated_at": "2014-09-01T09:10:11.000Z",
            "rating": 10,
            "type": "episode",
            "episode": {
                "season": 4,
                "number": 1,
                "title": "Box Cutter",
                "ids": {
                    "trakt": "49",
                    "tvdb": "2639411",
                    "imdb": "tt1683084",
                    "tmdb": "62118",
                },
            },
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {
                    "trakt": "1",
                    "slug": "breaking-bad",
                    "tvdb": "81189",
                    "imdb": "tt0903747",
                    "tmdb": "1396",
                },
            },
        }

        rating = TraktSyncRating.model_validate(rating_data)

        assert rating.rating == 10
        assert rating.type == "episode"
        assert rating.episode is not None
        assert rating.episode.season == 4
        assert rating.episode.number == 1
        assert rating.episode.title == "Box Cutter"

    def test_rating_validation_bounds(self):
        """Test rating validation with bounds checking."""
        # Valid ratings
        for valid_rating in [1, 5, 10]:
            rating = TraktSyncRating(
                rated_at="2014-09-01T09:10:11.000Z", rating=valid_rating, type="movie"
            )
            assert rating.rating == valid_rating

        # Invalid ratings
        for invalid_rating in [0, 11, -1, 15]:
            with pytest.raises(ValidationError) as exc_info:
                TraktSyncRating(
                    rated_at="2014-09-01T09:10:11.000Z",
                    rating=invalid_rating,
                    type="movie",
                )
            errors = exc_info.value.errors()
            assert any(
                error["type"] in ["greater_than_equal", "less_than_equal"]
                for error in errors
            )

    def test_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktSyncRating(**{})  # type: ignore[call-arg] # Testing: Pydantic validation with invalid types

        errors = exc_info.value.errors()
        assert len(errors) == 3  # rated_at, rating, type are required


class TestTraktSyncRatingItem:
    """Tests for the TraktSyncRatingItem model."""

    def test_valid_rating_item_for_add(self):
        """Test creating a rating item for add operation."""
        item_data: SyncRatingItemTestData = {
            "rating": 9,
            "rated_at": "2014-09-01T09:10:11.000Z",
            "title": "Inception",
            "year": 2010,
            "ids": {"trakt": "1", "imdb": "tt1375666", "tmdb": "27205"},
        }

        item = TraktSyncRatingItem(**item_data)

        assert item.rating == 9
        assert item.rated_at == "2014-09-01T09:10:11.000Z"
        assert item.title == "Inception"
        assert item.year == 2010
        assert item.ids is not None
        assert item.ids["trakt"] == "1"

    def test_valid_rating_item_for_remove(self):
        """Test creating a rating item for remove operation (no rating required)."""
        item_data: SyncRatingItemTestData = {
            "title": "Inception",
            "year": 2010,
            "ids": {"trakt": "1", "imdb": "tt1375666"},
        }

        item = TraktSyncRatingItem(**item_data)

        assert item.rating is None
        assert item.title == "Inception"
        assert item.year == 2010
        assert item.ids is not None

    def test_minimal_rating_item(self):
        """Test creating minimal rating item with just IDs."""
        item = TraktSyncRatingItem(ids={"trakt": "123"})

        assert item.rating is None
        assert item.title is None
        assert item.year is None
        assert item.ids == {"trakt": "123"}

    def test_rating_bounds_validation(self):
        """Test rating validation bounds for rating items."""
        # Valid ratings
        for valid_rating in [1, 5, 10]:
            item = TraktSyncRatingItem(rating=valid_rating, ids={"trakt": "123"})
            assert item.rating == valid_rating

        # Invalid ratings
        for invalid_rating in [0, 11, -1]:
            with pytest.raises(ValidationError) as exc_info:
                TraktSyncRatingItem(rating=invalid_rating, ids={"trakt": "123"})
            errors = exc_info.value.errors()
            assert any(
                error["type"] in ["greater_than_equal", "less_than_equal"]
                for error in errors
            )


class TestTraktSyncRatingsRequest:
    """Tests for the TraktSyncRatingsRequest model."""

    def test_movie_ratings_request(self):
        """Test creating a request with movie ratings."""
        movies = [
            TraktSyncRatingItem(
                rating=9, title="Inception", year=2010, ids={"imdb": "tt1375666"}
            )
        ]

        request = TraktSyncRatingsRequest(movies=movies)

        assert request.movies is not None
        assert len(request.movies) == 1
        assert request.movies[0].title == "Inception"
        assert request.shows is None
        assert request.seasons is None
        assert request.episodes is None

    def test_mixed_ratings_request(self):
        """Test creating a request with multiple content types."""
        movies = [TraktSyncRatingItem(rating=8, ids={"imdb": "tt1375666"})]
        shows = [TraktSyncRatingItem(rating=9, ids={"trakt": "123"})]

        request = TraktSyncRatingsRequest(movies=movies, shows=shows)

        assert request.movies is not None
        assert len(request.movies) == 1
        assert request.shows is not None
        assert len(request.shows) == 1
        assert request.seasons is None
        assert request.episodes is None

    def test_empty_request(self):
        """Test creating an empty request."""
        request = TraktSyncRatingsRequest()

        assert request.movies is None
        assert request.shows is None
        assert request.seasons is None
        assert request.episodes is None


class TestSyncRatingsSummaryCount:
    """Tests for the SyncRatingsSummaryCount model."""

    def test_default_counts(self):
        """Test default count values."""
        counts = SyncRatingsSummaryCount()

        assert counts.movies == 0
        assert counts.shows == 0
        assert counts.seasons == 0
        assert counts.episodes == 0

    def test_custom_counts(self):
        """Test creating with custom count values."""
        counts = SyncRatingsSummaryCount(movies=5, shows=3, seasons=2, episodes=10)

        assert counts.movies == 5
        assert counts.shows == 3
        assert counts.seasons == 2
        assert counts.episodes == 10


class TestSyncRatingsNotFound:
    """Tests for the SyncRatingsNotFound model."""

    def test_default_not_found(self):
        """Test default not found lists."""
        not_found = SyncRatingsNotFound()

        assert not_found.movies == []
        assert not_found.shows == []
        assert not_found.seasons == []
        assert not_found.episodes == []

    def test_not_found_with_items(self):
        """Test not found with actual items."""
        not_found_movie = TraktSyncRatingItem(rating=10, ids={"imdb": "tt0000111"})

        not_found = SyncRatingsNotFound(movies=[not_found_movie])

        assert len(not_found.movies) == 1
        assert not_found.movies[0].rating == 10
        assert not_found.shows == []


class TestSyncRatingsSummary:
    """Tests for the SyncRatingsSummary model."""

    def test_add_operation_summary(self):
        """Test summary for add operation."""
        added = SyncRatingsSummaryCount(movies=1, shows=1, seasons=1, episodes=2)
        not_found = SyncRatingsNotFound()

        summary = SyncRatingsSummary(added=added, not_found=not_found)

        assert summary.added is not None
        assert summary.added.movies == 1
        assert summary.added.shows == 1
        assert summary.removed is None
        assert summary.not_found.movies == []

    def test_remove_operation_summary(self):
        """Test summary for remove operation."""
        removed = SyncRatingsSummaryCount(movies=2, shows=1)
        not_found = SyncRatingsNotFound()

        summary = SyncRatingsSummary(removed=removed, not_found=not_found)

        assert summary.removed is not None
        assert summary.removed.movies == 2
        assert summary.removed.shows == 1
        assert summary.added is None

    def test_summary_with_not_found_items(self):
        """Test summary with not found items from API response."""
        not_found_item = TraktSyncRatingItem(rating=10, ids={"imdb": "tt0000111"})
        not_found = SyncRatingsNotFound(movies=[not_found_item])
        added = SyncRatingsSummaryCount(movies=1)

        summary = SyncRatingsSummary(added=added, not_found=not_found)

        assert summary.added is not None
        assert summary.added.movies == 1
        assert len(summary.not_found.movies) == 1
        assert summary.not_found.movies[0].rating == 10
