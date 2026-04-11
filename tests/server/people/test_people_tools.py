import asyncio
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from server.people.tools import (
    fetch_person_lists,
    fetch_person_movies,
    fetch_person_shows,
    fetch_person_summary,
)


@pytest.mark.asyncio
async def test_fetch_person_summary():
    sample_person = {
        "name": "Bryan Cranston",
        "ids": {
            "trakt": 142,
            "slug": "bryan-cranston",
            "imdb": "nm0186505",
            "tmdb": 17419,
        },
        "biography": "Bryan Lee Cranston is an American actor.",
        "birthday": "1956-03-07",
        "death": None,
        "birthplace": "San Fernando Valley, California, USA",
        "gender": "male",
        "known_for_department": "acting",
        "social_ids": {
            "twitter": "BryanCranston",
            "facebook": "thebryancranston",
            "instagram": "bryancranston",
            "wikipedia": None,
        },
    }

    with patch("server.people.tools.PersonSummaryClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_person)
        mock_client.get_person_extended.return_value = future

        result = await fetch_person_summary(person_id="bryan-cranston")

        assert "# Bryan Cranston" in result
        assert "1956-03-07" in result
        assert "San Fernando Valley" in result
        assert "Twitter: @BryanCranston" in result

        mock_client.get_person_extended.assert_called_once_with("bryan-cranston")


@pytest.mark.asyncio
async def test_fetch_person_summary_basic():
    sample_person = {
        "name": "Bryan Cranston",
        "ids": {
            "trakt": 142,
            "slug": "bryan-cranston",
            "imdb": "nm0186505",
            "tmdb": 17419,
        },
    }

    with patch("server.people.tools.PersonSummaryClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result(sample_person)
        mock_client.get_person.return_value = future

        result = await fetch_person_summary(person_id="bryan-cranston", extended=False)

        assert "# Bryan Cranston" in result
        assert "Trakt: 142" in result

        mock_client.get_person.assert_called_once_with("bryan-cranston")
        mock_client.get_person_extended.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_person_summary_string_error():
    with patch("server.people.tools.PersonSummaryClient") as mock_client_class:
        mock_client = mock_client_class.return_value

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("Not Found - person not found")
        mock_client.get_person_extended.return_value = future

        result = await fetch_person_summary(person_id="unknown-person")
        assert "# Error" in result


@pytest.mark.asyncio
async def test_fetch_person_movies():
    sample_credits = {
        "cast": [
            {
                "characters": ["Joe Brody"],
                "movie": {
                    "title": "Godzilla",
                    "year": 2014,
                    "ids": {"trakt": 24, "slug": "godzilla-2014"},
                },
            }
        ],
        "crew": {
            "production": [
                {
                    "jobs": ["Executive Producer"],
                    "movie": {
                        "title": "Godzilla",
                        "year": 2014,
                        "ids": {"trakt": 24, "slug": "godzilla-2014"},
                    },
                }
            ]
        },
    }

    sample_person = {
        "name": "Bryan Cranston",
        "ids": {"trakt": 142, "slug": "bryan-cranston"},
    }

    with (
        patch("server.people.tools.PersonMoviesClient") as mock_movies_class,
        patch("server.people.tools.PersonSummaryClient") as mock_summary_class,
    ):
        mock_movies = mock_movies_class.return_value
        mock_summary = mock_summary_class.return_value

        credits_future: asyncio.Future[Any] = asyncio.Future()
        credits_future.set_result(sample_credits)
        mock_movies.get_person_movies.return_value = credits_future

        person_future: asyncio.Future[Any] = asyncio.Future()
        person_future.set_result(sample_person)
        mock_summary.get_person.return_value = person_future

        result = await fetch_person_movies(person_id="bryan-cranston")

        assert "# Movie Credits for Bryan Cranston" in result
        assert "Godzilla" in result
        assert "Joe Brody" in result
        assert "Executive Producer" in result

        mock_movies.get_person_movies.assert_called_once_with("bryan-cranston")


@pytest.mark.asyncio
async def test_fetch_person_shows():
    sample_credits: dict[str, object] = {
        "cast": [
            {
                "characters": ["Walter White"],
                "episode_count": 62,
                "series_regular": True,
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "ids": {"trakt": 1, "slug": "breaking-bad"},
                },
            }
        ],
        "crew": {},
    }

    sample_person = {
        "name": "Bryan Cranston",
        "ids": {"trakt": 142, "slug": "bryan-cranston"},
    }

    with (
        patch("server.people.tools.PersonShowsClient") as mock_shows_class,
        patch("server.people.tools.PersonSummaryClient") as mock_summary_class,
    ):
        mock_shows = mock_shows_class.return_value
        mock_summary = mock_summary_class.return_value

        credits_future: asyncio.Future[Any] = asyncio.Future()
        credits_future.set_result(sample_credits)
        mock_shows.get_person_shows.return_value = credits_future

        person_future: asyncio.Future[Any] = asyncio.Future()
        person_future.set_result(sample_person)
        mock_summary.get_person.return_value = person_future

        result = await fetch_person_shows(person_id="bryan-cranston")

        assert "# Show Credits for Bryan Cranston" in result
        assert "Breaking Bad" in result
        assert "Walter White" in result
        assert "62 episodes" in result

        mock_shows.get_person_shows.assert_called_once_with("bryan-cranston")


@pytest.mark.asyncio
async def test_fetch_person_lists():
    sample_lists = [
        {
            "name": "Best Actors",
            "description": "The best actors in Hollywood",
            "item_count": 50,
            "likes": 99,
            "user": {"username": "filmfan"},
            "ids": {"trakt": 1337, "slug": "best-actors"},
        }
    ]

    sample_person = {
        "name": "Bryan Cranston",
        "ids": {"trakt": 142, "slug": "bryan-cranston"},
    }

    with (
        patch("server.people.tools.PersonListsClient") as mock_lists_class,
        patch("server.people.tools.PersonSummaryClient") as mock_summary_class,
    ):
        mock_lists = mock_lists_class.return_value
        mock_summary = mock_summary_class.return_value

        lists_future: asyncio.Future[Any] = asyncio.Future()
        lists_future.set_result(sample_lists)
        mock_lists.get_person_lists.return_value = lists_future

        person_future: asyncio.Future[Any] = asyncio.Future()
        person_future.set_result(sample_person)
        mock_summary.get_person.return_value = person_future

        result = await fetch_person_lists(person_id="bryan-cranston")

        assert "# Lists Containing Bryan Cranston" in result
        assert "Best Actors" in result
        assert "filmfan" in result
        assert "50 items" in result

        mock_lists.get_person_lists.assert_called_once_with(
            "bryan-cranston", list_type="all", sort="popular"
        )
