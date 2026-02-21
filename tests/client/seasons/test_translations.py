import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.seasons import SeasonsClient


@pytest.mark.asyncio
async def test_get_season_translations():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "Temporada 1",
            "overview": "La primera temporada.",
            "language": "es",
            "country": "es",
        },
        {
            "title": "Saison 1",
            "overview": "La premiere saison.",
            "language": "fr",
            "country": "fr",
        },
    ]
    mock_response.raise_for_status = MagicMock()

    mock_instance = MagicMock(spec=httpx.AsyncClient)
    mock_instance.get = AsyncMock(return_value=mock_response)
    mock_instance.post = AsyncMock()
    mock_instance.aclose = AsyncMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value = mock_instance

        client = SeasonsClient()
        result = await client.get_season_translations("game-of-thrones", 1)

        assert len(result) == 2
        assert result[0]["language"] == "es"
        assert result[0]["title"] == "Temporada 1"
        assert result[1]["language"] == "fr"

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert call_args[0][0].endswith(
            "/shows/game-of-thrones/seasons/1/translations/all"
        )

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_season_translations_explicit_language():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "Temporada 1",
            "overview": "La primera temporada.",
            "language": "es",
            "country": "es",
        },
    ]
    mock_response.raise_for_status = MagicMock()

    mock_instance = MagicMock(spec=httpx.AsyncClient)
    mock_instance.get = AsyncMock(return_value=mock_response)
    mock_instance.aclose = AsyncMock()

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch.dict(
            os.environ,
            {"TRAKT_CLIENT_ID": "test_id", "TRAKT_CLIENT_SECRET": "test_secret"},
        ),
    ):
        mock_client.return_value = mock_instance

        client = SeasonsClient()
        result = await client.get_season_translations("game-of-thrones", 1, "es")

        assert len(result) == 1
        assert result[0]["language"] == "es"

        mock_instance.get.assert_called_once()
        call_args = mock_instance.get.call_args
        assert call_args[0][0].endswith(
            "/shows/game-of-thrones/seasons/1/translations/es"
        )

        mock_response.raise_for_status.assert_called_once()
        mock_instance.aclose.assert_awaited_once()
