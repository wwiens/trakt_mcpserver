from unittest.mock import MagicMock

import pytest

from client.movies.people import MoviePeopleClient


@pytest.mark.asyncio
async def test_get_movie_people(
    trakt_env: None, patched_httpx_client: MagicMock
) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cast": [
            {
                "characters": ["Sam Flynn", "Clu"],
                "person": {
                    "name": "Jeff Bridges",
                    "ids": {
                        "trakt": 1,
                        "slug": "jeff-bridges",
                        "imdb": "nm0000313",
                        "tmdb": 1229,
                    },
                },
            }
        ],
        "crew": {
            "directing": [
                {
                    "jobs": ["Director"],
                    "person": {
                        "name": "Joseph Kosinski",
                        "ids": {
                            "trakt": 2,
                            "slug": "joseph-kosinski",
                        },
                    },
                }
            ]
        },
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    client = MoviePeopleClient()
    result = await client.get_movie_people("tron-legacy-2010")
    assert not isinstance(result, str)

    assert len(result["cast"]) == 1
    assert result["cast"][0]["person"]["name"] == "Jeff Bridges"
    assert "directing" in result.get("crew", {})

    patched_httpx_client.get.assert_called_once()
    call_args = patched_httpx_client.get.call_args
    assert "/movies/tron-legacy-2010/people" in call_args[0][0]


@pytest.mark.asyncio
async def test_get_movie_people_validates_empty_id(
    trakt_env: None, patched_httpx_client: MagicMock
) -> None:
    client = MoviePeopleClient()
    with pytest.raises(ValueError, match="movie_id cannot be empty"):
        await client.get_movie_people("   ")
