import os
from unittest.mock import MagicMock, patch

import pytest

from client.movies import MoviesClient


@pytest.mark.asyncio
async def test_get_movie_ratings():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "rating": 8.5,
        "votes": 2500,
        "distribution": {
            "10": 800,
            "9": 600,
            "8": 500,
            "7": 300,
            "6": 150,
            "5": 100,
            "4": 30,
            "3": 15,
            "2": 3,
            "1": 2,
        },
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        client = MoviesClient()
        result = await client.get_movie_ratings("1")

        assert isinstance(result, dict)
        assert result["rating"] == 8.5
        assert result["votes"] == 2500
        assert "distribution" in result
