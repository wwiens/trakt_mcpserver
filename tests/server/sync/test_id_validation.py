"""Tests for ID validation in sync tools."""

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from server.sync.tools import (
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
            invalid_items = [{"rating": 8, "trakt_id": invalid_id}]

            # Now expects ValidationError from Pydantic model creation
            with pytest.raises(ValidationError) as exc_info:
                await add_user_ratings(rating_type="movies", items=invalid_items)

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
            invalid_items = [{"rating": 7, "tmdb_id": invalid_id}]

            # Now expects ValidationError from Pydantic model creation
            with pytest.raises(ValidationError) as exc_info:
                await add_user_ratings(rating_type="movies", items=invalid_items)

            error = exc_info.value.errors()[0]
            assert error["type"] == "value_error"
            error_msg = error["msg"]
            assert "tmdb_id must be numeric" in error_msg
            assert invalid_id in error_msg

    @pytest.mark.asyncio
    async def test_add_user_ratings_invalid_trakt_id(self) -> None:
        """Test add_user_ratings with invalid trakt_id (upstream validation)."""
        invalid_items = [
            {"rating": 8, "trakt_id": "invalid_id", "title": "Test Movie", "year": 2023}
        ]

        # Now expects ValidationError from Pydantic model creation
        with pytest.raises(ValidationError) as exc_info:
            await add_user_ratings(rating_type="movies", items=invalid_items)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "trakt_id must be numeric" in error_msg
        assert "invalid_id" in error_msg

    @pytest.mark.asyncio
    async def test_add_user_ratings_invalid_tmdb_id(self) -> None:
        """Test add_user_ratings with invalid tmdb_id (upstream validation)."""
        invalid_items = [
            {"rating": 9, "tmdb_id": "not_numeric", "title": "Another Movie"}
        ]

        # Now expects ValidationError from Pydantic model creation
        with pytest.raises(ValidationError) as exc_info:
            await add_user_ratings(rating_type="movies", items=invalid_items)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "tmdb_id must be numeric" in error_msg
        assert "not_numeric" in error_msg

    @pytest.mark.asyncio
    async def test_add_user_ratings_valid_ids(self) -> None:
        """Test add_user_ratings with valid numeric IDs."""
        valid_items = [{"rating": 8, "trakt_id": "123", "tmdb_id": "456"}]

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
        invalid_items = [
            {"trakt_id": "bad_trakt_id", "title": "Movie to Remove", "year": 2022}
        ]

        # Now expects ValidationError from Pydantic model creation
        with pytest.raises(ValidationError) as exc_info:
            await remove_user_ratings(rating_type="movies", items=invalid_items)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "trakt_id must be numeric" in error_msg
        assert "bad_trakt_id" in error_msg

    @pytest.mark.asyncio
    async def test_remove_user_ratings_invalid_tmdb_id(self) -> None:
        """Test remove_user_ratings with invalid tmdb_id (upstream validation)."""
        invalid_items = [{"tmdb_id": "non.numeric", "title": "Remove This"}]

        # Now expects ValidationError from Pydantic model creation
        with pytest.raises(ValidationError) as exc_info:
            await remove_user_ratings(rating_type="shows", items=invalid_items)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        error_msg = error["msg"]
        assert "tmdb_id must be numeric" in error_msg
        assert "non.numeric" in error_msg

    @pytest.mark.asyncio
    async def test_remove_user_ratings_valid_ids(self) -> None:
        """Test remove_user_ratings with valid numeric IDs."""
        valid_items = [{"trakt_id": "789", "tmdb_id": "101112"}]

        with patch("server.sync.tools.SyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value

            # Mock successful response
            from models.sync.ratings import (
                SyncRatingsNotFound,
                SyncRatingsSummary,
                SyncRatingsSummaryCount,
            )

            summary_response = SyncRatingsSummary(
                removed=SyncRatingsSummaryCount(
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
        invalid_items = [{"rating": 7, "trakt_id": "invalid123"}]

        # Upstream validation provides clear error details
        with pytest.raises(ValidationError) as exc_info:
            await add_user_ratings(rating_type="movies", items=invalid_items)

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
        ],
    )
    @pytest.mark.asyncio
    async def test_multiple_validation_errors_parametrized(
        self, field: str, invalid_value: str, expected_message: str
    ) -> None:
        """Test that each invalid ID field generates the expected validation error."""
        invalid_items = [{"rating": 6, field: invalid_value}]

        with pytest.raises(ValidationError) as exc_info:
            await add_user_ratings(rating_type="movies", items=invalid_items)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert error["loc"] == (field,)
        error_msg = error["msg"]
        assert expected_message in error_msg
        assert invalid_value in error_msg
