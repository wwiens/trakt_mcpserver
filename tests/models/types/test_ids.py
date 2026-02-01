"""Tests for TraktIds Pydantic model."""

import pytest
from pydantic import ValidationError

from models.types.ids import TraktIds


class TestTraktIdsValidation:
    """Tests for TraktIds validation logic."""

    def test_all_fields_optional(self) -> None:
        """Test that empty TraktIds is valid."""
        ids = TraktIds()
        assert ids.trakt is None
        assert ids.slug is None
        assert ids.imdb is None
        assert ids.tmdb is None
        assert ids.tvdb is None

    def test_integer_coercion_from_string(self) -> None:
        """Test that numeric strings are coerced to integers."""
        # type: ignore comments needed because we're testing Pydantic coercion
        ids = TraktIds(
            trakt="12345",  # type: ignore[arg-type]
            tmdb="67890",  # type: ignore[arg-type]
            tvdb="11111",  # type: ignore[arg-type]
        )
        assert ids.trakt == 12345
        assert ids.tmdb == 67890
        assert ids.tvdb == 11111

    def test_integer_values_unchanged(self) -> None:
        """Test that integer values pass through."""
        ids = TraktIds(trakt=12345, tmdb=67890, tvdb=11111)
        assert ids.trakt == 12345
        assert ids.tmdb == 67890
        assert ids.tvdb == 11111

    def test_valid_imdb_format(self) -> None:
        """Test valid IMDB ID formats."""
        ids = TraktIds(imdb="tt0468569")
        assert ids.imdb == "tt0468569"

        ids2 = TraktIds(imdb="tt1375666")
        assert ids2.imdb == "tt1375666"

    def test_invalid_imdb_missing_prefix(self) -> None:
        """Test that IMDB IDs without 'tt' prefix are rejected."""
        with pytest.raises(ValidationError, match="imdb"):
            TraktIds(imdb="0468569")

    def test_invalid_imdb_non_numeric_suffix(self) -> None:
        """Test that IMDB IDs with non-numeric suffix are rejected."""
        with pytest.raises(ValidationError, match="imdb"):
            TraktIds(imdb="ttabcdef")

    def test_invalid_imdb_uppercase(self) -> None:
        """Test that uppercase 'TT' prefix is rejected."""
        with pytest.raises(ValidationError, match="imdb"):
            TraktIds(imdb="TT0468569")

    def test_slug_accepts_any_string(self) -> None:
        """Test that slug accepts any string."""
        ids = TraktIds(slug="breaking-bad-2008")
        assert ids.slug == "breaking-bad-2008"

        ids2 = TraktIds(slug="the-dark-knight")
        assert ids2.slug == "the-dark-knight"

    def test_invalid_numeric_string_rejected(self) -> None:
        """Test that non-numeric strings for int fields are rejected."""
        with pytest.raises(ValidationError, match="trakt"):
            TraktIds(trakt="not-a-number")  # type: ignore[arg-type]

        with pytest.raises(ValidationError, match="tmdb"):
            TraktIds(tmdb="abc123")  # type: ignore[arg-type]

        with pytest.raises(ValidationError, match="tvdb"):
            TraktIds(tvdb="12.34")  # type: ignore[arg-type]


class TestTraktIdsFromApiData:
    """Tests for TraktIds parsing from API response data."""

    def test_parse_movie_ids(self) -> None:
        """Test parsing typical movie IDs from API."""
        ids = TraktIds(
            trakt=16662,
            slug="inception-2010",
            imdb="tt1375666",
            tmdb=27205,
        )
        assert ids.trakt == 16662
        assert ids.slug == "inception-2010"
        assert ids.imdb == "tt1375666"
        assert ids.tmdb == 27205
        assert ids.tvdb is None

    def test_parse_show_ids_with_tvdb(self) -> None:
        """Test parsing show IDs including tvdb."""
        ids = TraktIds(
            trakt=1388,
            slug="breaking-bad",
            tvdb=81189,
            imdb="tt0903747",
            tmdb=1396,
        )
        assert ids.trakt == 1388
        assert ids.slug == "breaking-bad"
        assert ids.tvdb == 81189
        assert ids.imdb == "tt0903747"
        assert ids.tmdb == 1396

    def test_parse_with_null_values(self) -> None:
        """Test parsing IDs with null values."""
        ids = TraktIds(
            trakt=62315,
            slug="some-show",
            tvdb=4849873,
            imdb=None,
            tmdb=None,
        )
        assert ids.trakt == 62315
        assert ids.slug == "some-show"
        assert ids.tvdb == 4849873
        assert ids.imdb is None
        assert ids.tmdb is None

    def test_parse_minimal_ids(self) -> None:
        """Test parsing with minimal ID fields."""
        ids = TraktIds(trakt=12345, slug="test-item")
        assert ids.trakt == 12345
        assert ids.slug == "test-item"
        assert ids.imdb is None
        assert ids.tmdb is None
        assert ids.tvdb is None
