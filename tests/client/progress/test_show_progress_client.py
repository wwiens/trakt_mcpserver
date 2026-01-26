"""Tests for the ShowProgressClient."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from client.progress.client import ProgressClient
    from models.progress.show_progress import ShowProgressResponse


class TestShowProgressClient:
    """Tests for ShowProgressClient.get_show_progress()."""

    @pytest.mark.asyncio
    async def test_get_show_progress_success(
        self,
        authenticated_progress_client: ProgressClient,
        sample_show_progress_response: ShowProgressResponse,
    ) -> None:
        """Test successful retrieval of show progress."""
        with patch.object(
            authenticated_progress_client, "_make_typed_request"
        ) as mock_request:
            mock_request.return_value = sample_show_progress_response

            result = await authenticated_progress_client.get_show_progress(
                "breaking-bad"
            )

            assert result["aired"] == 62
            assert result["completed"] == 45
            assert result["next_episode"]["season"] == 2
            assert result["next_episode"]["number"] == 11
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_show_progress_with_specials(
        self,
        authenticated_progress_client: ProgressClient,
        sample_show_progress_response: ShowProgressResponse,
    ) -> None:
        """Test retrieval with specials parameter."""
        with patch.object(
            authenticated_progress_client, "_make_typed_request"
        ) as mock_request:
            mock_request.return_value = sample_show_progress_response

            await authenticated_progress_client.get_show_progress(
                "breaking-bad",
                specials=True,
                count_specials=True,
            )

            # Verify the params include specials settings
            call_kwargs = mock_request.call_args
            params = call_kwargs.kwargs.get("params", {})
            assert params["specials"] == "true"
            assert params["count_specials"] == "true"

    @pytest.mark.asyncio
    async def test_get_show_progress_with_hidden(
        self,
        authenticated_progress_client: ProgressClient,
        sample_show_progress_response: ShowProgressResponse,
    ) -> None:
        """Test retrieval with hidden seasons parameter."""
        with patch.object(
            authenticated_progress_client, "_make_typed_request"
        ) as mock_request:
            mock_request.return_value = sample_show_progress_response

            await authenticated_progress_client.get_show_progress(
                "breaking-bad",
                hidden=True,
            )

            # Verify the params include hidden setting
            call_kwargs = mock_request.call_args
            params = call_kwargs.kwargs.get("params", {})
            assert params["hidden"] == "true"

    @pytest.mark.asyncio
    async def test_get_show_progress_not_authenticated(
        self,
        authenticated_progress_client: ProgressClient,
    ) -> None:
        """Test that unauthenticated requests raise ValueError."""
        # Remove authentication
        authenticated_progress_client.auth_token = None

        with pytest.raises(ValueError, match="authenticated"):
            await authenticated_progress_client.get_show_progress("breaking-bad")

    @pytest.mark.asyncio
    async def test_get_show_progress_url_encoding(
        self,
        authenticated_progress_client: ProgressClient,
        sample_show_progress_response: ShowProgressResponse,
    ) -> None:
        """Test that show IDs with special characters are properly URL-encoded."""
        with patch.object(
            authenticated_progress_client, "_make_typed_request"
        ) as mock_request:
            mock_request.return_value = sample_show_progress_response

            # Use a show ID with special characters
            await authenticated_progress_client.get_show_progress("show/with:special")

            # Verify the endpoint was called (URL encoding happens internally)
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            # The endpoint should have the show_id URL-encoded
            endpoint = (
                call_args.args[0]
                if call_args.args
                else call_args.kwargs.get("endpoint", "")
            )
            assert "show%2Fwith%3Aspecial" in endpoint

    @pytest.mark.asyncio
    async def test_get_show_progress_last_activity_watched(
        self,
        authenticated_progress_client: ProgressClient,
        sample_show_progress_response: ShowProgressResponse,
    ) -> None:
        """Test retrieval with last_activity='watched' parameter."""
        with patch.object(
            authenticated_progress_client, "_make_typed_request"
        ) as mock_request:
            mock_request.return_value = sample_show_progress_response

            await authenticated_progress_client.get_show_progress(
                "breaking-bad",
                last_activity="watched",
            )

            # Verify the params include last_activity setting
            call_kwargs = mock_request.call_args
            params = call_kwargs.kwargs.get("params", {})
            assert params["last_activity"] == "watched"
