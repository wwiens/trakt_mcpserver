"""Tests for UserRatingIdentifier validation (removal operations)."""

from typing import Any

import pytest
from pydantic import ValidationError

from server.sync.tools import UserRatingIdentifier


class TestUserRatingIdentifierValidation:
    """Test validation logic for UserRatingIdentifier (removal operations)."""

    @pytest.mark.parametrize(
        "kwargs,expected",
        [
            pytest.param(
                {"trakt_id": "123"},
                {
                    "trakt_id": "123",
                    "imdb_id": None,
                    "tmdb_id": None,
                    "title": None,
                    "year": None,
                },
                id="trakt_id_only",
            ),
            pytest.param(
                {"imdb_id": "tt1234567"},
                {
                    "trakt_id": None,
                    "imdb_id": "tt1234567",
                    "tmdb_id": None,
                    "title": None,
                    "year": None,
                },
                id="imdb_id_only",
            ),
            pytest.param(
                {"tmdb_id": "456"},
                {
                    "trakt_id": None,
                    "imdb_id": None,
                    "tmdb_id": "456",
                    "title": None,
                    "year": None,
                },
                id="tmdb_id_only",
            ),
            pytest.param(
                {"title": "Inception", "year": 2010},
                {
                    "trakt_id": None,
                    "imdb_id": None,
                    "tmdb_id": None,
                    "title": "Inception",
                    "year": 2010,
                },
                id="title_and_year",
            ),
            pytest.param(
                {"trakt_id": "123", "imdb_id": "tt1234567", "tmdb_id": "456"},
                {
                    "trakt_id": "123",
                    "imdb_id": "tt1234567",
                    "tmdb_id": "456",
                    "title": None,
                    "year": None,
                },
                id="multiple_identifiers",
            ),
            pytest.param(
                {"trakt_id": "123", "title": "Inception", "year": 2010},
                {
                    "trakt_id": "123",
                    "imdb_id": None,
                    "tmdb_id": None,
                    "title": "Inception",
                    "year": 2010,
                },
                id="identifier_and_title_year",
            ),
        ],
    )
    def test_valid_identifiers(
        self, kwargs: dict[str, Any], expected: dict[str, Any]
    ) -> None:
        """Test valid identifier configurations."""
        item = UserRatingIdentifier(**kwargs)

        for field, expected_value in expected.items():
            assert getattr(item, field) == expected_value

    def test_invalid_no_identifiers_no_title_year(self) -> None:
        """Test validation error when no identifiers or title/year provided."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier()

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "Rating item must include either an identifier" in error_msg
        assert "trakt_id, slug, imdb_id, tmdb_id, or tvdb_id" in error_msg
        assert "or both title and year" in error_msg

    def test_invalid_title_without_year(self) -> None:
        """Test validation error when title provided without year."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(title="Inception")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "Rating item must include either an identifier" in error_msg

    def test_invalid_year_without_title(self) -> None:
        """Test validation error when year provided without title."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(year=2010)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
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

        # Verify the model has the expected fields from IdentifierValidatorMixin
        expected_fields = {
            "trakt_id",
            "slug",
            "imdb_id",
            "tmdb_id",
            "tvdb_id",
            "title",
            "year",
        }
        actual_fields = set(UserRatingIdentifier.model_fields.keys())
        assert actual_fields == expected_fields
