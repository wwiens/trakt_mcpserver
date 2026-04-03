from unittest.mock import MagicMock

import pytest

from client.shows.people import ShowPeopleClient


@pytest.mark.asyncio
async def test_get_show_people(
    trakt_env: None, patched_httpx_client: MagicMock
) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cast": [
            {
                "characters": ["Walter White"],
                "episode_count": 62,
                "person": {
                    "name": "Bryan Cranston",
                    "ids": {"trakt": 142, "slug": "bryan-cranston"},
                },
            }
        ],
        "crew": {
            "production": [
                {
                    "jobs": ["Executive Producer"],
                    "episode_count": 62,
                    "person": {
                        "name": "Vince Gilligan",
                        "ids": {
                            "trakt": 1,
                            "slug": "vince-gilligan",
                        },
                    },
                }
            ]
        },
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    client = ShowPeopleClient()
    result = await client.get_show_people("breaking-bad")

    assert len(result["cast"]) == 1
    assert result["cast"][0]["person"]["name"] == "Bryan Cranston"
    assert "production" in result["crew"]

    patched_httpx_client.get.assert_called_once()
    call_args = patched_httpx_client.get.call_args
    assert "/shows/breaking-bad/people" in call_args[0][0]
    assert call_args[1].get("params") is None


@pytest.mark.asyncio
async def test_get_show_people_with_guest_stars(
    trakt_env: None, patched_httpx_client: MagicMock
) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cast": [],
        "guest_stars": [
            {
                "characters": ["Hank Schrader"],
                "person": {
                    "name": "Dean Norris",
                    "ids": {"trakt": 2, "slug": "dean-norris"},
                },
            }
        ],
        "crew": {},
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    client = ShowPeopleClient()
    result = await client.get_show_people("breaking-bad", include_guest_stars=True)

    assert len(result["guest_stars"]) == 1

    call_args = patched_httpx_client.get.call_args
    assert call_args[1].get("params") == {"extended": "guest_stars"}


@pytest.mark.asyncio
async def test_get_show_people_validates_empty_id(
    trakt_env: None, patched_httpx_client: MagicMock
) -> None:
    client = ShowPeopleClient()
    with pytest.raises(ValueError, match="show_id cannot be empty"):
        await client.get_show_people("   ")
