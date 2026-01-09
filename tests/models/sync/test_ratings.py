"""Tests for the models.sync.ratings module."""

from datetime import datetime
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

    def test_valid_season_creation(self) -> None:
        """Test creating a valid TraktSeason instance."""
        season = TraktSeason(
            number=1, ids={"trakt": "140912", "tvdb": "703353", "tmdb": "81266"}
        )

        assert season.number == 1
        assert season.ids is not None
        assert season.ids["trakt"] == "140912"
        assert season.ids["tvdb"] == "703353"
        assert season.ids["tmdb"] == "81266"

    def test_season_without_ids(self) -> None:
        """Test creating season without IDs."""
        season = TraktSeason(number=2)
        assert season.number == 2
        assert season.ids is None


class TestTraktSyncRating:
    """Tests for the TraktSyncRating model."""

    def test_valid_movie_rating_creation(self) -> None:
        """Test creating a valid movie rating from API response data."""
        rating_data: SyncRatingTestData = {
            "rated_at": datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
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

        assert rating.rated_at == datetime.fromisoformat(
            "2014-09-01T09:10:11.000+00:00"
        )
        assert rating.rating == 10
        assert rating.type == "movie"
        assert rating.movie is not None
        assert rating.movie.title == "TRON: Legacy"
        assert rating.movie.year == 2010
        assert rating.show is None
        assert rating.season is None
        assert rating.episode is None

    def test_valid_show_rating_creation(self) -> None:
        """Test creating a valid show rating from API response data."""
        rating_data: SyncRatingTestData = {
            "rated_at": datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
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

        assert rating.rated_at == datetime.fromisoformat(
            "2014-09-01T09:10:11.000+00:00"
        )
        assert rating.rating == 10
        assert rating.type == "show"
        assert rating.show is not None
        assert rating.show.title == "Breaking Bad"
        assert rating.show.year == 2008
        assert rating.movie is None

    def test_valid_season_rating_creation(self) -> None:
        """Test creating a valid season rating from API response data."""
        rating_data: SyncRatingTestData = {
            "rated_at": datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
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

        assert rating.rated_at == datetime.fromisoformat(
            "2014-09-01T09:10:11.000+00:00"
        )
        assert rating.rating == 8
        assert rating.type == "season"
        assert rating.season is not None
        assert rating.season.number == 1
        assert rating.show is not None
        assert rating.show.title == "Breaking Bad"

    def test_valid_episode_rating_creation(self) -> None:
        """Test creating a valid episode rating from API response data."""
        rating_data: SyncRatingTestData = {
            "rated_at": datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
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

    def test_rating_validation_bounds(self) -> None:
        """Test rating validation with bounds checking."""
        # Valid ratings
        for valid_rating in [1, 5, 10]:
            rating = TraktSyncRating(
                rated_at=datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
                rating=valid_rating,
                type="movie",
            )
            assert rating.rating == valid_rating

        # Invalid ratings
        for invalid_rating in [0, 11, -1, 15]:
            with pytest.raises(ValidationError) as exc_info:
                TraktSyncRating(
                    rated_at=datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
                    rating=invalid_rating,
                    type="movie",
                )
            errors = exc_info.value.errors()
            assert any(
                error["type"] in ["greater_than_equal", "less_than_equal"]
                for error in errors
            )

    def test_required_fields(self) -> None:
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktSyncRating(**{})  # type: ignore[call-arg] # Testing: Pydantic validation with invalid types

        errors = exc_info.value.errors()
        missing = {
            tuple(err.get("loc", ())) for err in errors if err.get("type") == "missing"
        }
        required = {("rated_at",), ("rating",), ("type",)}
        assert required.issubset(missing), (
            f"Missing required fields not all reported: {errors}"
        )


class TestTraktSyncRatingItem:
    """Tests for the TraktSyncRatingItem model."""

    def test_valid_rating_item_for_add(self) -> None:
        """Test creating a rating item for add operation."""
        item_data: SyncRatingItemTestData = {
            "rating": 9,
            "rated_at": datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
            "title": "Inception",
            "year": 2010,
            "ids": {"trakt": "1", "imdb": "tt1375666", "tmdb": "27205"},
        }

        item = TraktSyncRatingItem(**item_data)

        assert item.rating == 9
        assert item.rated_at == datetime.fromisoformat("2014-09-01T09:10:11.000+00:00")
        assert item.title == "Inception"
        assert item.year == 2010
        assert item.ids is not None
        assert item.ids["trakt"] == "1"

    def test_valid_rating_item_for_remove(self) -> None:
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

    def test_minimal_rating_item(self) -> None:
        """Test creating minimal rating item with just IDs."""
        item = TraktSyncRatingItem(ids={"trakt": "123"})

        assert item.rating is None
        assert item.title is None
        assert item.year is None
        assert item.ids == {"trakt": "123"}

    def test_rating_bounds_validation(self) -> None:
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

    def test_movie_ratings_request(self) -> None:
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

    def test_mixed_ratings_request(self) -> None:
        """Test that requests with multiple content types are rejected."""
        movies = [TraktSyncRatingItem(rating=8, ids={"imdb": "tt1375666"})]
        shows = [TraktSyncRatingItem(rating=9, ids={"trakt": "123"})]

        with pytest.raises(ValidationError) as exc_info:
            TraktSyncRatingsRequest(movies=movies, shows=shows)

        error = exc_info.value.errors()[0]
        assert error["type"] == "ratings.multiple_collections"
        assert "Only one ratings list allowed per request" in error["msg"]

    def test_empty_request(self) -> None:
        """Test that empty requests are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TraktSyncRatingsRequest()

        error = exc_info.value.errors()[0]
        assert error["type"] == "ratings.collection_missing"
        assert "At least one ratings list must be provided" in error["msg"]


class TestSyncRatingsSummaryCount:
    """Tests for the SyncRatingsSummaryCount model."""

    def test_default_counts(self) -> None:
        """Test default count values."""
        counts = SyncRatingsSummaryCount()

        assert counts.movies == 0
        assert counts.shows == 0
        assert counts.seasons == 0
        assert counts.episodes == 0

    def test_custom_counts(self) -> None:
        """Test creating with custom count values."""
        counts = SyncRatingsSummaryCount(movies=5, shows=3, seasons=2, episodes=10)

        assert counts.movies == 5
        assert counts.shows == 3
        assert counts.seasons == 2
        assert counts.episodes == 10


class TestSyncRatingsNotFound:
    """Tests for the SyncRatingsNotFound model."""

    def test_default_not_found(self) -> None:
        """Test default not found lists."""
        not_found = SyncRatingsNotFound.model_construct()

        assert not_found.movies == []
        assert not_found.shows == []
        assert not_found.seasons == []
        assert not_found.episodes == []

    def test_not_found_with_items(self) -> None:
        """Test not found with actual items."""
        not_found_movie = TraktSyncRatingItem(rating=10, ids={"imdb": "tt0000111"})

        not_found = SyncRatingsNotFound(
            movies=[not_found_movie], shows=[], seasons=[], episodes=[]
        )

        assert len(not_found.movies) == 1
        assert not_found.movies[0].rating == 10
        assert not_found.shows == []


class TestSyncRatingsSummary:
    """Tests for the SyncRatingsSummary model."""

    def test_add_operation_summary(self) -> None:
        """Test summary for add operation."""
        added = SyncRatingsSummaryCount(movies=1, shows=1, seasons=1, episodes=2)
        not_found = SyncRatingsNotFound.model_construct()

        summary = SyncRatingsSummary(added=added, not_found=not_found)

        assert summary.added is not None
        assert summary.added.movies == 1
        assert summary.added.shows == 1
        assert summary.deleted is None
        assert summary.not_found.movies == []

    def test_remove_operation_summary(self) -> None:
        """Test summary for remove operation."""
        deleted = SyncRatingsSummaryCount(movies=2, shows=1)
        not_found = SyncRatingsNotFound.model_construct()

        summary = SyncRatingsSummary(deleted=deleted, not_found=not_found)

        assert summary.deleted is not None
        assert summary.deleted.movies == 2
        assert summary.deleted.shows == 1
        assert summary.added is None

    def test_summary_with_not_found_items(self) -> None:
        """Test summary with not found items from API response."""
        not_found_item = TraktSyncRatingItem(rating=10, ids={"imdb": "tt0000111"})
        not_found = SyncRatingsNotFound(
            movies=[not_found_item], shows=[], seasons=[], episodes=[]
        )
        added = SyncRatingsSummaryCount(movies=1)

        summary = SyncRatingsSummary(added=added, not_found=not_found)

        assert summary.added is not None
        assert summary.added.movies == 1
        assert len(summary.not_found.movies) == 1
        assert summary.not_found.movies[0].rating == 10


class TestComprehensiveValidation:
    """Comprehensive validation tests for sync ratings models."""

    @pytest.mark.parametrize("rating", [1, 10])
    def test_boundary_ratings_valid(self, rating: int) -> None:
        """Test boundary rating values (1, 10) are accepted."""
        sync_rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
            rating=rating,
            type="movie",
        )
        assert sync_rating.rating == rating

    @pytest.mark.parametrize("rating", [0, -1, 11, 15])
    def test_boundary_ratings_invalid(self, rating: int) -> None:
        """Test invalid rating values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TraktSyncRating(
                rated_at=datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
                rating=rating,
                type="movie",
            )
        errors = exc_info.value.errors()
        assert any(
            error["type"] in ["greater_than_equal", "less_than_equal"]
            for error in errors
        )

    @pytest.mark.parametrize("year", [1900, 2024, 2030])
    def test_valid_years_accepted(self, year: int) -> None:
        """Test plausible year values are accepted."""
        item = TraktSyncRatingItem(rating=5, title="Test Movie", year=year)
        assert item.year == year

    def test_negative_year_handling(self) -> None:
        """Test that years must be reasonable (> 1800)."""
        # Verify year validation rejects unreasonable values
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc:
            TraktSyncRatingItem(
                rating=5,
                title="Test Movie",
                year=-100,  # Should be rejected
            )
        assert "greater than 1800" in str(exc.value).lower()

        # Valid year should work
        item = TraktSyncRatingItem(rating=5, title="Test Movie", year=1850)
        assert item.year == 1850

    def test_non_negative_count_constraints(self) -> None:
        """Test that count fields enforce non-negative constraints."""
        # Valid non-negative counts
        valid_count = SyncRatingsSummaryCount(
            movies=0, shows=5, seasons=10, episodes=20
        )
        assert valid_count.movies == 0
        assert valid_count.shows == 5

        # Test negative counts are rejected
        with pytest.raises(ValidationError) as exc_info:
            SyncRatingsSummaryCount(movies=-1)

        errors = exc_info.value.errors()
        assert any(error["type"] == "greater_than_equal" for error in errors)

    def test_nested_seasons_empty_list_vs_none(self) -> None:
        """Test handling of empty list vs None for nested seasons."""
        # Empty list
        item_empty_list = TraktSyncRatingItem(
            rating=8, title="Show with empty seasons", seasons=[]
        )
        assert item_empty_list.seasons == []

        # None (default)
        item_none = TraktSyncRatingItem(rating=8, title="Show with no seasons")
        assert item_none.seasons is None

    def test_nested_episodes_validation(self) -> None:
        """Test nested episode rating validation."""
        from models.sync.ratings import TraktSyncEpisodeRating, TraktSyncSeasonRating

        # Valid nested structure
        episode = TraktSyncEpisodeRating(rating=9, number=1)
        season = TraktSyncSeasonRating(number=1, episodes=[episode])
        item = TraktSyncRatingItem(
            rating=8, title="Show with episodes", seasons=[season]
        )

        assert item.seasons is not None
        assert len(item.seasons) == 1
        assert item.seasons[0].episodes is not None
        assert len(item.seasons[0].episodes) == 1
        assert item.seasons[0].episodes[0].rating == 9

    @pytest.mark.parametrize("rating_type", ["movies", "shows", "seasons", "episodes"])
    def test_sync_ratings_request_all_types(self, rating_type: str) -> None:
        """Test TraktSyncRatingsRequest with each content type."""
        item = TraktSyncRatingItem(rating=7, title="Test Item")

        # Create request with single type populated
        request_data = {rating_type: [item]}
        request = TraktSyncRatingsRequest(**request_data)

        # Verify only the specified type has data
        for attr_name in ["movies", "shows", "seasons", "episodes"]:
            attr_value = getattr(request, attr_name)
            if attr_name == rating_type:
                assert attr_value == [item]
            else:
                assert attr_value is None

    def test_default_factory_behavior(self) -> None:
        """Test that default_factory creates independent list instances."""
        not_found_1 = SyncRatingsNotFound.model_construct()
        not_found_2 = SyncRatingsNotFound.model_construct()

        # Lists should be independent instances
        assert not_found_1.movies is not not_found_2.movies
        assert not_found_1.shows is not not_found_2.shows

        # Adding to one shouldn't affect the other
        not_found_1.movies.append(TraktSyncRatingItem(title="Test"))
        assert len(not_found_1.movies) == 1
        assert len(not_found_2.movies) == 0

    def test_datetime_timezone_handling(self) -> None:
        """Test datetime timezone handling in rated_at field."""
        # Test with UTC timezone
        utc_datetime = datetime.fromisoformat("2014-09-01T09:10:11.000+00:00")
        rating = TraktSyncRating(rated_at=utc_datetime, rating=8, type="movie")
        assert rating.rated_at.tzinfo is not None

        # Test with different timezone
        tz_datetime = datetime.fromisoformat("2014-09-01T09:10:11.000-05:00")
        rating_tz = TraktSyncRating(rated_at=tz_datetime, rating=8, type="movie")
        assert rating_tz.rated_at.tzinfo is not None

    @pytest.mark.parametrize("content_type", ["movie", "show", "season", "episode"])
    def test_sync_rating_type_field_validation(self, content_type: str) -> None:
        """Test that type field accepts all valid literal values."""
        rating = TraktSyncRating(
            rated_at=datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
            rating=5,
            type=content_type,  # type: ignore[arg-type]
        )
        assert rating.type == content_type

    def test_sync_rating_invalid_type_rejected(self) -> None:
        """Test that invalid type values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TraktSyncRating(
                rated_at=datetime.fromisoformat("2014-09-01T09:10:11.000+00:00"),
                rating=5,
                type="invalid_type",  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any("literal_error" in error["type"] for error in errors)
