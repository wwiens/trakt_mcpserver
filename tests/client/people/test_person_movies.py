from unittest.mock import MagicMock

import pytest

from client.people import PeopleClient


@pytest.mark.asyncio
async def test_get_person_movies(trakt_env: None, patched_httpx_client: MagicMock):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cast": [
            {
                "characters": ["Joe Brody"],
                "movie": {
                    "title": "Godzilla",
                    "year": 2014,
                    "ids": {
                        "trakt": 24,
                        "slug": "godzilla-2014",
                        "imdb": "tt0831387",
                        "tmdb": 124905,
                    },
                },
            }
        ],
        "crew": {
            "directing": [
                {
                    "jobs": ["Director"],
                    "movie": {
                        "title": "Godzilla",
                        "year": 2014,
                        "ids": {
                            "trakt": 24,
                            "slug": "godzilla-2014",
                            "imdb": "tt0831387",
                            "tmdb": 124905,
                        },
                    },
                }
            ]
        },
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    client = PeopleClient()
    result = await client.get_person_movies("bryan-cranston")
    assert not isinstance(result, str)

    assert len(result["cast"]) == 1
    assert result["cast"][0]["movie"]["title"] == "Godzilla"
    assert result["cast"][0]["characters"] == ["Joe Brody"]
    assert "directing" in result.get("crew", {})

    patched_httpx_client.get.assert_called_once()
    call_args = patched_httpx_client.get.call_args
    assert "/people/bryan-cranston/movies" in call_args[0][0]
