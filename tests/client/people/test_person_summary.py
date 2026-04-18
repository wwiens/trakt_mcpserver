from unittest.mock import MagicMock

import pytest

from client.people import PeopleClient


@pytest.mark.asyncio
async def test_get_person(trakt_env: None, patched_httpx_client: MagicMock):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "name": "Bryan Cranston",
        "ids": {
            "trakt": 142,
            "slug": "bryan-cranston",
            "imdb": "nm0186505",
            "tmdb": 17419,
        },
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    client = PeopleClient()
    result = await client.get_person("bryan-cranston")
    assert not isinstance(result, str)

    assert result["name"] == "Bryan Cranston"
    assert result["ids"]["trakt"] == 142

    patched_httpx_client.get.assert_called_once()
    call_args = patched_httpx_client.get.call_args
    assert "/people/bryan-cranston" in call_args[0][0]


@pytest.mark.asyncio
async def test_get_person_extended(trakt_env: None, patched_httpx_client: MagicMock):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "name": "Bryan Cranston",
        "ids": {
            "trakt": 142,
            "slug": "bryan-cranston",
            "imdb": "nm0186505",
            "tmdb": 17419,
        },
        "social_ids": {
            "twitter": "BryanCranston",
            "facebook": "thebryancranston",
            "instagram": "bryancranston",
            "wikipedia": None,
        },
        "biography": "Bryan Lee Cranston is an American actor.",
        "birthday": "1956-03-07",
        "death": None,
        "birthplace": "San Fernando Valley, California, USA",
        "homepage": "http://www.bryancranston.com/",
        "gender": "male",
        "known_for_department": "acting",
        "updated_at": "2022-11-03T17:00:54.000Z",
    }
    mock_response.raise_for_status = MagicMock()
    patched_httpx_client.get.return_value = mock_response

    client = PeopleClient()
    result = await client.get_person_extended("bryan-cranston")
    assert not isinstance(result, str)

    assert result["name"] == "Bryan Cranston"
    assert result.get("biography") == "Bryan Lee Cranston is an American actor."
    assert result.get("gender") == "male"

    patched_httpx_client.get.assert_called_once()
    call_args = patched_httpx_client.get.call_args
    assert "/people/bryan-cranston" in call_args[0][0]
    assert call_args[1].get("params") == {"extended": "full"}


@pytest.mark.asyncio
async def test_get_person_validates_empty_id(
    trakt_env: None, patched_httpx_client: MagicMock
):
    client = PeopleClient()
    with pytest.raises(ValueError, match="person_id cannot be empty"):
        await client.get_person("   ")
