"""Tests for UserRatingRequestItem model validation."""

import pytest
from pydantic import ValidationError

from server.sync.tools import UserRatingRequestItem


class TestUserRatingRequestItemValidation:
    """Test validation logic for UserRatingRequestItem."""

    def test_valid_with_trakt_id(self) -> None:
        """Test valid request with trakt_id identifier."""
        item = UserRatingRequestItem(rating=8, trakt_id="123")
        assert item.rating == 8
        assert item.trakt_id == "123"
        assert item.imdb_id is None
        assert item.tmdb_id is None
        assert item.title is None
        assert item.year is None

    def test_valid_with_imdb_id(self) -> None:
        """Test valid request with imdb_id identifier."""
        item = UserRatingRequestItem(rating=9, imdb_id="tt1234567")
        assert item.rating == 9
        assert item.imdb_id == "tt1234567"
        assert item.trakt_id is None
        assert item.tmdb_id is None
        assert item.title is None
        assert item.year is None

    def test_valid_with_tmdb_id(self) -> None:
        """Test valid request with tmdb_id identifier."""
        item = UserRatingRequestItem(rating=7, tmdb_id="456")
        assert item.rating == 7
        assert item.tmdb_id == "456"
        assert item.trakt_id is None
        assert item.imdb_id is None
        assert item.title is None
        assert item.year is None

    def test_valid_with_title_and_year(self) -> None:
        """Test valid request with title and year."""
        item = UserRatingRequestItem(rating=10, title="Inception", year=2010)
        assert item.rating == 10
        assert item.title == "Inception"
        assert item.year == 2010
        assert item.trakt_id is None
        assert item.imdb_id is None
        assert item.tmdb_id is None

    def test_valid_with_multiple_identifiers(self) -> None:
        """Test valid request with multiple identifiers."""
        item = UserRatingRequestItem(
            rating=6, trakt_id="123", imdb_id="tt1234567", tmdb_id="456"
        )
        assert item.rating == 6
        assert item.trakt_id == "123"
        assert item.imdb_id == "tt1234567"
        assert item.tmdb_id == "456"

    def test_valid_with_identifier_and_title_year(self) -> None:
        """Test valid request with both identifier and title/year."""
        item = UserRatingRequestItem(
            rating=5, trakt_id="123", title="Inception", year=2010
        )
        assert item.rating == 5
        assert item.trakt_id == "123"
        assert item.title == "Inception"
        assert item.year == 2010

    def test_invalid_no_identifiers_no_title_year(self) -> None:
        """Test validation error when no identifiers or title/year provided."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=8)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = str(error.get("ctx", {}).get("error", ""))
        assert "Rating item must include either an identifier" in error_msg
        assert "trakt_id, imdb_id, or tmdb_id" in error_msg
        assert "or both title and year" in error_msg

    def test_invalid_title_without_year(self) -> None:
        """Test validation error when title provided without year."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=8, title="Inception")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = str(error.get("ctx", {}).get("error", ""))
        assert "Rating item must include either an identifier" in error_msg

    def test_invalid_year_without_title(self) -> None:
        """Test validation error when year provided without title."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=8, year=2010)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = str(error.get("ctx", {}).get("error", ""))
        assert "Rating item must include either an identifier" in error_msg

    def test_invalid_empty_strings_no_title_year(self) -> None:
        """Test validation error when identifiers are empty strings and no title/year."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=8, trakt_id="", imdb_id="", tmdb_id="")

        # Empty strings should be caught by min_length validation on fields
        # and then cross-field validation should also fail
        errors = exc_info.value.errors()
        assert len(errors) >= 1  # At least one validation error

    def test_invalid_whitespace_strings_no_title_year(self) -> None:
        """Test validation error when identifiers are whitespace and no title/year."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=8, trakt_id="   ", imdb_id="  ", tmdb_id=" ")

        # Whitespace strings fail min_length validation before stripping occurs
        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_short"
        assert error["loc"] == ("trakt_id",)

    def test_valid_after_string_stripping(self) -> None:
        """Test validation passes after string stripping."""
        item = UserRatingRequestItem(rating=8, trakt_id="  123  ")
        assert item.trakt_id == "123"  # Should be stripped

    def test_field_validation_rating_bounds(self) -> None:
        """Test field validation for rating bounds."""
        # Test minimum rating (1)
        item = UserRatingRequestItem(rating=1, trakt_id="123")
        assert item.rating == 1

        # Test maximum rating (10)
        item = UserRatingRequestItem(rating=10, trakt_id="123")
        assert item.rating == 10

        # Test invalid rating too low
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=0, trakt_id="123")

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than_equal"
        assert error["loc"] == ("rating",)

        # Test invalid rating too high
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=11, trakt_id="123")

        error = exc_info.value.errors()[0]
        assert error["type"] == "less_than_equal"
        assert error["loc"] == ("rating",)

    def test_field_validation_year_bounds(self) -> None:
        """Test field validation for year bounds."""
        # Valid year
        item = UserRatingRequestItem(rating=8, title="Movie", year=2023)
        assert item.year == 2023

        # Invalid year too low
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=8, title="Movie", year=1800)

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than"
        assert error["loc"] == ("year",)

    def test_field_validation_string_min_length(self) -> None:
        """Test field validation for string minimum length."""
        # Test empty string validation for identifiers
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=8, trakt_id="")

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_short"
        assert error["loc"] == ("trakt_id",)

        # Test empty string validation for title
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=8, title="", year=2023)

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_short"
        assert error["loc"] == ("title",)
