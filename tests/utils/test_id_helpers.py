"""Tests for ID helper utilities."""

import pytest

from utils.api.id_helpers import build_trakt_id_object


class TestBuildTraktIdObject:
    """Tests for build_trakt_id_object function."""

    def test_numeric_trakt_id_movie(self) -> None:
        """Test building ID object with numeric Trakt ID for movies."""
        result = build_trakt_id_object("12345", "movies")

        assert result == {"movies": [{"ids": {"trakt": 12345}}]}

    def test_numeric_trakt_id_show(self) -> None:
        """Test building ID object with numeric Trakt ID for shows."""
        result = build_trakt_id_object("67890", "shows")

        assert result == {"shows": [{"ids": {"trakt": 67890}}]}

    def test_imdb_id_movie(self) -> None:
        """Test building ID object with IMDB ID for movies."""
        result = build_trakt_id_object("tt1104001", "movies")

        assert result == {"movies": [{"ids": {"imdb": "tt1104001"}}]}

    def test_imdb_id_show(self) -> None:
        """Test building ID object with IMDB ID for shows."""
        result = build_trakt_id_object("tt0903747", "shows")

        assert result == {"shows": [{"ids": {"imdb": "tt0903747"}}]}

    def test_slug_movie(self) -> None:
        """Test building ID object with slug for movies."""
        result = build_trakt_id_object("tron-legacy-2010", "movies")

        assert result == {"movies": [{"ids": {"slug": "tron-legacy-2010"}}]}

    def test_slug_show(self) -> None:
        """Test building ID object with slug for shows."""
        result = build_trakt_id_object("breaking-bad", "shows")

        assert result == {"shows": [{"ids": {"slug": "breaking-bad"}}]}

    def test_slug_with_numbers_not_treated_as_trakt_id(self) -> None:
        """Test that slugs containing numbers are treated as slugs, not Trakt IDs."""
        result = build_trakt_id_object("2001-a-space-odyssey-1968", "movies")

        # Should be treated as slug because it contains non-digit characters
        assert result == {"movies": [{"ids": {"slug": "2001-a-space-odyssey-1968"}}]}

    def test_imdb_id_with_leading_zeros(self) -> None:
        """Test IMDB IDs with leading zeros are handled correctly."""
        result = build_trakt_id_object("tt0000001", "movies")

        assert result == {"movies": [{"ids": {"imdb": "tt0000001"}}]}

    def test_empty_item_id_raises_value_error(self) -> None:
        """Test that empty item_id raises ValueError."""
        with pytest.raises(ValueError, match="item_id cannot be empty"):
            build_trakt_id_object("", "movies")
