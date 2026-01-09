"""Tests for ID validation in sync tools."""

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from server.sync.tools import (
    UserRatingIdentifier,
    UserRatingRequestItem,
    add_user_ratings,
    remove_user_ratings,
)


class TestIDValidationInSyncTools:
    """Test ID validation in the main sync tool functions."""

    @pytest.mark.asyncio
    async def test_trakt_id_validation_mixed_characters(self) -> None:
        """Test various invalid trakt_id formats (upstream validation)."""
        invalid_trakt_ids = ["123abc", "abc123", "12.34", "1-23", "12 34", "x1y2z3"]

        for invalid_id in invalid_trakt_ids:
            # Now validation happens at model creation
            with pytest.raises(ValidationError) as exc_info:
                UserRatingRequestItem(rating=8, trakt_id=invalid_id)

            error = exc_info.value.errors()[0]
            assert error["type"] == "value_error"
            error_msg = error["msg"]
            assert "trakt_id must be numeric" in error_msg
            assert invalid_id in error_msg

    @pytest.mark.asyncio
    async def test_tmdb_id_validation_mixed_characters(self) -> None:
        """Test various invalid tmdb_id formats (upstream validation)."""
        invalid_tmdb_ids = ["456def", "def456", "45.67", "4-56", "45 67", "a1b2c3"]

        for invalid_id in invalid_tmdb_ids:
            # Now validation happens at model creation
            with pytest.raises(ValidationError) as exc_info:
                UserRatingRequestItem(rating=7, tmdb_id=invalid_id)

            error = exc_info.value.errors()[0]
            assert error["type"] == "value_error"
            error_msg = error["msg"]
            assert "tmdb_id must be numeric" in error_msg
            assert invalid_id in error_msg

    @pytest.mark.asyncio
    async def test_add_user_ratings_invalid_trakt_id(self) -> None:
        """Test add_user_ratings with invalid trakt_id (upstream validation)."""
        # Now validation happens at model creation
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(
                rating=8, trakt_id="invalid_id", title="Test Movie", year=2023
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "trakt_id must be numeric" in error_msg
        assert "invalid_id" in error_msg

    @pytest.mark.asyncio
    async def test_add_user_ratings_invalid_tmdb_id(self) -> None:
        """Test add_user_ratings with invalid tmdb_id (upstream validation)."""
        # Now validation happens at model creation
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(
                rating=9, tmdb_id="not_numeric", title="Another Movie"
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "tmdb_id must be numeric" in error_msg
        assert "not_numeric" in error_msg

    @pytest.mark.asyncio
    async def test_add_user_ratings_valid_ids(self) -> None:
        """Test add_user_ratings with valid numeric IDs."""
        valid_items = [UserRatingRequestItem(rating=8, trakt_id="123", tmdb_id="456")]

        with patch("server.sync.tools.SyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Mock successful response
            from models.sync.ratings import (
                SyncRatingsNotFound,
                SyncRatingsSummary,
                SyncRatingsSummaryCount,
            )

            summary_response = SyncRatingsSummary(
                added=SyncRatingsSummaryCount(movies=1, shows=0, seasons=0, episodes=0),
                not_found=SyncRatingsNotFound(
                    movies=[], shows=[], seasons=[], episodes=[]
                ),
            )
            mock_client.add_sync_ratings = AsyncMock(return_value=summary_response)

            result = await add_user_ratings(rating_type="movies", items=valid_items)

            # Verify the function completed successfully
            assert "Successfully added **1** movies rating(s)" in result

            # Verify client was called and check the IDs were properly converted
            mock_client.add_sync_ratings.assert_called_once()
            call_args = mock_client.add_sync_ratings.call_args[0][0]
            assert hasattr(call_args, "movies")
            assert call_args.movies is not None
            assert len(call_args.movies) == 1

            movie_item = call_args.movies[0]
            assert movie_item.ids["trakt"] == 123  # Should be integer
            assert movie_item.ids["tmdb"] == 456  # Should be integer

    @pytest.mark.asyncio
    async def test_remove_user_ratings_invalid_trakt_id(self) -> None:
        """Test remove_user_ratings with invalid trakt_id (upstream validation)."""
        # Now validation happens at model creation
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(
                trakt_id="bad_trakt_id", title="Movie to Remove", year=2022
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "trakt_id must be numeric" in error_msg
        assert "bad_trakt_id" in error_msg

    @pytest.mark.asyncio
    async def test_remove_user_ratings_invalid_tmdb_id(self) -> None:
        """Test remove_user_ratings with invalid tmdb_id (upstream validation)."""
        # Now validation happens at model creation
        with pytest.raises(ValidationError) as exc_info:
            UserRatingIdentifier(tmdb_id="non.numeric", title="Remove This")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "tmdb_id must be numeric" in error_msg
        assert "non.numeric" in error_msg

    @pytest.mark.asyncio
    async def test_remove_user_ratings_valid_ids(self) -> None:
        """Test remove_user_ratings with valid numeric IDs."""
        valid_items = [UserRatingIdentifier(trakt_id="789", tmdb_id="101112")]

        with patch("server.sync.tools.SyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Mock successful response
            from models.sync.ratings import (
                SyncRatingsNotFound,
                SyncRatingsSummary,
                SyncRatingsSummaryCount,
            )

            summary_response = SyncRatingsSummary(
                deleted=SyncRatingsSummaryCount(
                    movies=1, shows=0, seasons=0, episodes=0
                ),
                not_found=SyncRatingsNotFound(
                    movies=[], shows=[], seasons=[], episodes=[]
                ),
            )
            mock_client.remove_sync_ratings = AsyncMock(return_value=summary_response)

            result = await remove_user_ratings(rating_type="movies", items=valid_items)

            # Verify the function completed successfully
            assert "Successfully removed **1** movies rating(s)" in result

            # Verify client was called and check the IDs were properly converted
            mock_client.remove_sync_ratings.assert_called_once()
            call_args = mock_client.remove_sync_ratings.call_args[0][0]
            assert hasattr(call_args, "movies")
            assert call_args.movies is not None
            assert len(call_args.movies) == 1

            movie_item = call_args.movies[0]
            assert movie_item.ids["trakt"] == 789  # Should be integer
            assert movie_item.ids["tmdb"] == 101112  # Should be integer

    @pytest.mark.asyncio
    async def test_pydantic_validation_error_details(self) -> None:
        """Test that Pydantic validation provides clear error details."""
        # Upstream validation provides clear error details
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=7, trakt_id="invalid123")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert error["loc"] == ("trakt_id",)
        error_msg = error["msg"]
        assert "trakt_id must be numeric" in error_msg
        assert "invalid123" in error_msg

    @pytest.mark.parametrize(
        "field,invalid_value,expected_message",
        [
            ("trakt_id", "bad_trakt", "trakt_id must be numeric"),
            ("tmdb_id", "bad_tmdb", "tmdb_id must be numeric"),
            ("tvdb_id", "bad_tvdb", "tvdb_id must be numeric"),
            ("imdb_id", "invalid", "imdb_id must be in format 'tt' followed by digits"),
            ("imdb_id", "tt", "imdb_id must be in format 'tt' followed by digits"),
            ("imdb_id", "123456", "imdb_id must be in format 'tt' followed by digits"),
        ],
    )
    @pytest.mark.asyncio
    async def test_multiple_validation_errors_parametrized(
        self, field: str, invalid_value: str, expected_message: str
    ) -> None:
        """Test that each invalid ID field generates the expected validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRatingRequestItem(rating=6, **{field: invalid_value})  # type: ignore[arg-type]

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert error["loc"] == (field,)
        error_msg = error["msg"]
        assert expected_message in error_msg

    @pytest.mark.asyncio
    async def test_tvdb_id_validation_mixed_characters(self) -> None:
        """Test various invalid tvdb_id formats (upstream validation)."""
        invalid_tvdb_ids = ["789ghi", "ghi789", "78.90", "7-89", "78 90"]

        for invalid_id in invalid_tvdb_ids:
            with pytest.raises(ValidationError) as exc_info:
                UserRatingRequestItem(rating=7, tvdb_id=invalid_id)

            error = exc_info.value.errors()[0]
            assert error["type"] == "value_error"
            error_msg = error["msg"]
            assert "tvdb_id must be numeric" in error_msg
            assert invalid_id in error_msg

    @pytest.mark.asyncio
    async def test_imdb_id_format_validation(self) -> None:
        """Test IMDB ID format validation (must be tt followed by digits)."""
        invalid_imdb_ids = ["tt", "123456", "TT123456", "tt123abc", "imdb123"]

        for invalid_id in invalid_imdb_ids:
            with pytest.raises(ValidationError) as exc_info:
                UserRatingRequestItem(rating=8, imdb_id=invalid_id)

            error = exc_info.value.errors()[0]
            assert error["type"] == "value_error"
            error_msg = error["msg"]
            assert "imdb_id must be in format 'tt' followed by digits" in error_msg
            assert invalid_id in error_msg

    @pytest.mark.asyncio
    async def test_valid_imdb_id_format(self) -> None:
        """Test that valid IMDB IDs are accepted."""
        valid_imdb_ids = ["tt0372784", "tt1234567", "tt00001"]

        for imdb_id in valid_imdb_ids:
            # Should not raise validation error
            item = UserRatingRequestItem(rating=9, imdb_id=imdb_id)
            assert item.imdb_id == imdb_id

    @pytest.mark.asyncio
    async def test_slug_id_accepted(self) -> None:
        """Test that slug identifier is accepted."""
        item = UserRatingRequestItem(rating=8, slug="the-dark-knight-2008")
        assert item.slug == "the-dark-knight-2008"

    @pytest.mark.asyncio
    async def test_tvdb_id_valid(self) -> None:
        """Test that valid numeric tvdb_id is accepted."""
        item = UserRatingRequestItem(rating=7, tvdb_id="12345")
        assert item.tvdb_id == "12345"

    @pytest.mark.asyncio
    async def test_all_new_ids_in_identifier(self) -> None:
        """Test that slug and tvdb_id work in UserRatingIdentifier."""
        # Test slug
        item_slug = UserRatingIdentifier(slug="breaking-bad")
        assert item_slug.slug == "breaking-bad"

        # Test tvdb_id
        item_tvdb = UserRatingIdentifier(tvdb_id="81189")
        assert item_tvdb.tvdb_id == "81189"

        # Test valid imdb_id
        item_imdb = UserRatingIdentifier(imdb_id="tt0903747")
        assert item_imdb.imdb_id == "tt0903747"
