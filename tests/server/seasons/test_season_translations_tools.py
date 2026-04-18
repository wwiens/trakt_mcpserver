import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.seasons.tools import fetch_season_translations


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_language",
    ["english", "xyz", "123", "", "e", "abc"],
)
async def test_fetch_season_translations_invalid_language(invalid_language: str):
    result = await fetch_season_translations(
        show_id="game-of-thrones", season=1, language=invalid_language
    )
    assert "# Error" in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "valid_language",
    ["en", "es", "all", "ALL", "En", "  fr  "],
)
async def test_fetch_season_translations_valid_language(valid_language: str):
    sample_translations = [
        {
            "title": "Season 1",
            "overview": "The first season.",
            "language": "en",
            "country": "us",
        },
    ]

    with (
        patch("server.seasons.tools.SeasonTranslationsClient") as mock_client_class,
        patch(
            "server.seasons.tools._get_show_title",
            new_callable=AsyncMock,
            return_value="Game of Thrones",
        ),
    ):
        mock_client = mock_client_class.return_value
        mock_client.get_season_translations = AsyncMock(
            return_value=sample_translations
        )

        result = await fetch_season_translations(
            show_id="game-of-thrones", season=1, language=valid_language
        )

        assert "Game of Thrones" in result
        mock_client.get_season_translations.assert_called_once()
