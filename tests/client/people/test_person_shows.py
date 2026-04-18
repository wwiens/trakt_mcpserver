from unittest.mock import MagicMock

import pytest

from client.people import PeopleClient


@pytest.mark.asyncio
async def test_get_person_shows(trakt_env: None, patched_httpx_client: MagicMock):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cast": [
            {
                "characters": ["Walter White"],
                "episode_count": 62,
                "series_regular": True,
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "ids": {
                        "trakt": 1,
                        "slug": "breaking-bad",
                        "tvdb": 81189,
                        "imdb": "tt0903747",
                        "tmdb": 1396,
                    },
                },
            }
        ],
        "crew": {
            "production": [
                {
                    "jobs": ["Producer"],
                    "show": {
                        "title": "Breaking Bad",
                        "year": 2008,
                        "ids": {
                            "trakt": 1,
                            "slug": "breaking-bad",
                            "tvdb": 81189,
                            "imdb": "tt0903747",
                            "tmdb": 1396,
                        },
                    },
                }
            ]
        },
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    client = PeopleClient()
    result = await client.get_person_shows("bryan-cranston")
    assert not isinstance(result, str)

    assert len(result["cast"]) == 1
    assert result["cast"][0]["show"]["title"] == "Breaking Bad"
    assert result["cast"][0].get("episode_count") == 62
    assert result["cast"][0].get("series_regular") is True
    assert "production" in result.get("crew", {})

    patched_httpx_client.get.assert_called_once()
    call_args = patched_httpx_client.get.call_args
    assert "/people/bryan-cranston/shows" in call_args[0][0]
