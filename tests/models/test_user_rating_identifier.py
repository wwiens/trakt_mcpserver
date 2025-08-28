"""Tests for UserRatingIdentifier validation (removal operations)."""

import pytest
from pydantic import ValidationError

from server.sync.tools import UserRatingIdentifier


class TestUserRatingIdentifierValidation:
    """Test validation logic for UserRatingIdentifier (removal operations)."""

    def test_valid_with_trakt_id(self) -> None:
        """Test valid identifier with trakt_id."""
        item = UserRatingIdentifier(trakt_id="123")
        assert item.trakt_id == "123"
        assert item.imdb_id is None
        assert item.tmdb_id is None
        assert item.title is None
        assert item.year is None

    def test_valid_with_imdb_id(self) -> None:
        """Test valid identifier with imdb_id."""
        item = UserRatingIdentifier(imdb_id="tt1234567")
        assert item.imdb_id == "tt1234567"
        assert item.trakt_id is None
        assert item.tmdb_id is None
        assert item.title is None
        assert item.year is None

    def test_valid_with_tmdb_id(self) -> None:
        """Test valid identifier with tmdb_id."""
        item = UserRatingIdentifier(tmdb_id="456")
        assert item.tmdb_id == "456"
        assert item.trakt_id is None
        assert item.imdb_id is None
        assert item.title is None
        assert item.year is None

    def test_valid_with_title_and_year(self) -> None:
        """Test valid identifier with title and year."""
        item = UserRatingIdentifier(title="Inception", year=2010)
        assert item.title == "Inception"
        assert item.year == 2010
        assert item.trakt_id is None
        assert item.imdb_id is None
        assert item.tmdb_id is None

    def test_valid_with_multiple_identifiers(self) -> None:
        """Test valid identifier with multiple IDs."""
        item = UserRatingIdentifier(trakt_id="123", imdb_id="tt1234567", tmdb_id="456")
        assert item.trakt_id == "123"
        assert item.imdb_id == "tt1234567"
        assert item.tmdb_id == "456"

    def test_valid_with_identifier_and_title_year(self) -> None:
        """Test valid identifier with both ID and title/year."""
        item = UserRatingIdentifier(trakt_id="123", title="Inception", year=2010)
        assert item.trakt_id == "123"
        assert item.title == "Inception"
        assert item.year == 2010

    def test_invalid_no_identifiers_no_title_year(self) -> None:
        """Test validation error when no identifiers or title/year provided."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier()

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = str(error.get("ctx", {}).get("error", ""))
        assert "Rating item must include either an identifier" in error_msg
        assert "trakt_id, imdb_id, or tmdb_id" in error_msg
        assert "or both title and year" in error_msg

    def test_invalid_title_without_year(self) -> None:
        """Test validation error when title provided without year."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(title="Inception")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = str(error.get("ctx", {}).get("error", ""))
        assert "Rating item must include either an identifier" in error_msg

    def test_invalid_year_without_title(self) -> None:
        """Test validation error when year provided without title."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(year=2010)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = str(error.get("ctx", {}).get("error", ""))
        assert "Rating item must include either an identifier" in error_msg

    def test_invalid_empty_strings_no_title_year(self) -> None:
        """Test validation error when identifiers are empty strings and no title/year."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(trakt_id="", imdb_id="", tmdb_id="")

        # Empty strings should be caught by min_length validation on fields
        errors = exc_info.value.errors()
        assert len(errors) >= 1  # At least one validation error

    def test_valid_after_string_stripping(self) -> None:
        """Test validation passes after string stripping."""
        item = UserRatingIdentifier(trakt_id="  123  ")
        assert item.trakt_id == "123"  # Should be stripped

    def test_field_validation_year_bounds(self) -> None:
        """Test field validation for year bounds."""
        # Valid year
        item = UserRatingIdentifier(title="Movie", year=2023)
        assert item.year == 2023

        # Invalid year too low
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(title="Movie", year=1800)

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than"
        assert error["loc"] == ("year",)

    def test_field_validation_string_min_length(self) -> None:
        """Test field validation for string minimum length."""
        # Test empty string validation for identifiers
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(trakt_id="")

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_short"
        assert error["loc"] == ("trakt_id",)

        # Test empty string validation for title
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(title="", year=2023)

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_short"
        assert error["loc"] == ("title",)

    def test_cross_field_validation_precedence(self) -> None:
        """Test that cross-field validation runs after field validation."""
        # Field validation should catch empty strings first
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(trakt_id="", title="", year=2023)

        # Should get field validation errors first
        errors = exc_info.value.errors()
        error_types = [error["type"] for error in errors]
        assert "string_too_short" in error_types
        # Cross-field validation may not even run if field validation fails

    def test_no_rating_field_for_removal(self) -> None:
        """Test that UserRatingIdentifier doesn't have a rating field (removal only)."""
        # This should work - no rating field required for removal
        item = UserRatingIdentifier(trakt_id="123")

        # Verify no rating field exists
        assert not hasattr(item, "rating")

        # Verify the model only has the expected fields
        expected_fields = {"trakt_id", "imdb_id", "tmdb_id", "title", "year"}
        actual_fields = set(UserRatingIdentifier.model_fields.keys())
        assert actual_fields == expected_fields
