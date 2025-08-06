"""Tests for the models.user module."""

from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from models.shows import TraktShow
from models.user import TraktUserShow

if TYPE_CHECKING:
    from tests.models.test_data_types import SeasonData, ShowTestData, UserShowTestData


class TestTraktUserShow:
    """Tests for the TraktUserShow model."""

    def test_valid_user_show_creation(self):
        """Test creating a valid TraktUserShow instance."""
        show_data: ShowTestData = {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": "1", "slug": "breaking-bad"},
            "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
        }

        user_show_data: UserShowTestData = {
            "show": show_data,
            "last_watched_at": "2023-01-15T20:30:00Z",
            "last_updated_at": "2023-01-16T10:00:00Z",
            "plays": 5,
        }

        user_show = TraktUserShow(**user_show_data)  # type: ignore[arg-type] # Testing: Type validation

        assert user_show.show.title == "Breaking Bad"
        assert user_show.show.year == 2008
        assert user_show.last_watched_at == "2023-01-15T20:30:00Z"
        assert user_show.last_updated_at == "2023-01-16T10:00:00Z"
        assert user_show.plays == 5
        assert user_show.seasons is None

    def test_user_show_with_seasons(self):
        """Test creating user show with seasons data."""
        show_data: ShowTestData = {
            "title": "Game of Thrones",
            "year": 2011,
            "ids": {"trakt": "1390"},
        }

        seasons_data: list[SeasonData] = [
            {
                "number": 1,
                "episodes": [
                    {
                        "number": 1,
                        "completed": True,
                        "last_watched_at": "2023-01-01T20:00:00Z",
                    },
                    {
                        "number": 2,
                        "completed": True,
                        "last_watched_at": "2023-01-02T20:00:00Z",
                    },
                ],
            },
            {
                "number": 2,
                "episodes": [
                    {
                        "number": 1,
                        "completed": True,
                        "last_watched_at": "2023-01-03T20:00:00Z",
                    },
                ],
            },
        ]

        user_show_data: UserShowTestData = {
            "show": show_data,
            "last_watched_at": "2023-01-15T20:30:00Z",
            "last_updated_at": "2023-01-16T10:00:00Z",
            "plays": 10,
            "seasons": seasons_data,
        }

        user_show = TraktUserShow(**user_show_data)  # type: ignore[arg-type] # Testing: Complex season data structure

        assert user_show.show.title == "Game of Thrones"
        assert user_show.seasons is not None
        assert len(user_show.seasons) == 2
        assert user_show.seasons[0]["number"] == 1
        assert len(user_show.seasons[0]["episodes"]) == 2
        assert user_show.plays == 10

    def test_user_show_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktUserShow()  # type: ignore[call-arg] # Testing: Pydantic validation with invalid types

        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}

        # Check all required fields are present
        expected_required = {"show", "last_watched_at", "last_updated_at", "plays"}
        assert expected_required.issubset(required_fields)

    def test_user_show_missing_show(self):
        """Test that show field is required."""
        with pytest.raises(ValidationError) as exc_info:
            TraktUserShow(  # type: ignore[call-arg] # Testing: Type validation
                last_watched_at="2023-01-15T20:30:00Z",
                last_updated_at="2023-01-16T10:00:00Z",
                plays=5,
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("show",) for error in errors)

    def test_user_show_missing_timestamps(self):
        """Test that timestamp fields are required."""
        show_data = {
            "title": "Breaking Bad",
            "ids": {"trakt": "1"},
        }

        with pytest.raises(ValidationError) as exc_info:
            TraktUserShow(show=show_data, plays=5)  # type: ignore[arg-type,call-arg] # Testing: Type validation

        errors = exc_info.value.errors()
        error_fields = {error["loc"][0] for error in errors}
        assert "last_watched_at" in error_fields
        assert "last_updated_at" in error_fields

    def test_user_show_missing_plays(self):
        """Test that plays field is required."""
        show_data = {
            "title": "Breaking Bad",
            "ids": {"trakt": "1"},
        }

        with pytest.raises(ValidationError) as exc_info:
            TraktUserShow(  # type: ignore[arg-type,call-arg] # Testing: Type validation
                show=show_data,
                last_watched_at="2023-01-15T20:30:00Z",
                last_updated_at="2023-01-16T10:00:00Z",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("plays",) for error in errors)

    def test_user_show_field_types(self):
        """Test that fields have correct types."""
        show_data = {
            "title": "Breaking Bad",
            "ids": {"trakt": "1"},
        }

        # Test wrong type for plays
        with pytest.raises(ValidationError):
            TraktUserShow(
                show=show_data,  # type: ignore[arg-type] # Testing: Type validation
                last_watched_at="2023-01-15T20:30:00Z",
                last_updated_at="2023-01-16T10:00:00Z",
                plays=["not", "an", "int"],  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types
            )

        # Test wrong type for last_watched_at
        with pytest.raises(ValidationError):
            TraktUserShow(
                show=show_data,  # type: ignore[arg-type] # Testing: Type validation
                last_watched_at=["not", "a", "string"],  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types
                last_updated_at="2023-01-16T10:00:00Z",
                plays=5,
            )

        # Test wrong type for seasons
        with pytest.raises(ValidationError):
            TraktUserShow(
                show=show_data,  # type: ignore[arg-type] # Testing: Type validation
                last_watched_at="2023-01-15T20:30:00Z",
                last_updated_at="2023-01-16T10:00:00Z",
                plays=5,
                seasons="not_a_list",  # type: ignore[arg-type] # Testing: Should be list
            )

    def test_user_show_nested_show_validation(self):
        """Test that nested show validation works."""
        # Missing required show fields
        invalid_show_data = {
            "title": "Breaking Bad",
            # Missing required 'ids' field
        }

        with pytest.raises(ValidationError):
            TraktUserShow(
                show=invalid_show_data,  # type: ignore[arg-type] # Testing: Type validation
                last_watched_at="2023-01-15T20:30:00Z",
                last_updated_at="2023-01-16T10:00:00Z",
                plays=5,
            )

    def test_user_show_serialization(self):
        """Test that TraktUserShow can be serialized."""
        show_data: ShowTestData = {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": "1"},
            "overview": "Great show",
        }

        user_show_data: UserShowTestData = {
            "show": show_data,
            "last_watched_at": "2023-01-15T20:30:00Z",
            "last_updated_at": "2023-01-16T10:00:00Z",
            "plays": 5,
            "seasons": None,
        }

        user_show = TraktUserShow(**user_show_data)  # type: ignore[arg-type] # Testing: Type validation
        serialized = user_show.model_dump()

        assert serialized == user_show_data

    def test_user_show_json_serialization(self):
        """Test that TraktUserShow can be serialized to JSON."""
        show_data: ShowTestData = {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": "1"},
            "overview": "Great show",
        }

        user_show_data: UserShowTestData = {
            "show": show_data,
            "last_watched_at": "2023-01-15T20:30:00Z",
            "last_updated_at": "2023-01-16T10:00:00Z",
            "plays": 5,
        }

        user_show = TraktUserShow(**user_show_data)  # type: ignore[arg-type] # Testing: Type validation
        json_str = user_show.model_dump_json()

        # Should be valid JSON
        import json

        parsed = json.loads(json_str)

        expected = {
            **user_show_data,
            "seasons": None,  # Default value should be included
        }
        assert parsed == expected

    def test_user_show_with_traktshow_instance(self):
        """Test creating TraktUserShow with TraktShow instance."""
        show = TraktShow(
            title="Breaking Bad",
            year=2008,
            ids={"trakt": "1"},
            overview="Great show",
        )

        user_show = TraktUserShow(
            show=show,
            last_watched_at="2023-01-15T20:30:00Z",
            last_updated_at="2023-01-16T10:00:00Z",
            plays=5,
        )

        assert user_show.show.title == "Breaking Bad"
        assert user_show.show.year == 2008
        assert isinstance(user_show.show, TraktShow)

    def test_user_show_complex_seasons_data(self):
        """Test user show with complex seasons data structure."""
        show_data: ShowTestData = {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": "1"},
        }

        complex_seasons: list[SeasonData] = [
            {
                "number": 1,
                "aired": 7,
                "completed": 7,
                "episodes": [
                    {
                        "number": 1,
                        "plays": 1,
                        "last_watched_at": "2023-01-01T20:00:00Z",
                        "completed": True,
                    },
                    {
                        "number": 2,
                        "plays": 1,
                        "last_watched_at": "2023-01-02T20:00:00Z",
                        "completed": True,
                    },
                    {
                        "number": 3,
                        "plays": 2,
                        "last_watched_at": "2023-01-03T20:00:00Z",
                        "completed": True,
                    },
                ],
            }
        ]

        user_show_data: UserShowTestData = {
            "show": show_data,
            "last_watched_at": "2023-01-15T20:30:00Z",
            "last_updated_at": "2023-01-16T10:00:00Z",
            "plays": 15,
            "seasons": complex_seasons,
        }

        user_show = TraktUserShow(**user_show_data)  # type: ignore[arg-type] # Testing: Complex season data structure

        assert user_show.seasons is not None
        assert len(user_show.seasons) == 1
        season = user_show.seasons[0]
        assert season["number"] == 1
        # Note: aired and completed are test-only fields, not in actual API response
        assert len(season["episodes"]) == 3

        # Check first episode
        episode = season["episodes"][0]
        assert episode["number"] == 1
        assert episode.get("plays") == 1
        # Note: completed is a test-only field, not in actual API response

    def test_user_show_empty_seasons(self):
        """Test user show with empty seasons list."""
        show_data: ShowTestData = {
            "title": "New Show",
            "ids": {"trakt": "999"},
        }

        user_show_data: UserShowTestData = {
            "show": show_data,
            "last_watched_at": "2023-01-15T20:30:00Z",
            "last_updated_at": "2023-01-16T10:00:00Z",
            "plays": 0,
            "seasons": [],  # Empty list
        }

        user_show = TraktUserShow(**user_show_data)  # type: ignore[arg-type] # Testing: Type validation

        assert user_show.seasons == []
        assert user_show.plays == 0

    def test_user_show_from_api_response(self):
        """Test creating user show from typical API response."""
        # Simulate typical API response from Trakt
        api_response: dict[str, object] = {
            "last_watched_at": "2023-12-01T21:00:00.000Z",
            "last_updated_at": "2023-12-01T21:05:00.000Z",
            "plays": 62,
            "reset_at": None,
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
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family's future before he dies.",
            },
            "seasons": [
                {
                    "number": 1,
                    "episodes": [
                        {
                            "number": 1,
                            "plays": 1,
                            "last_watched_at": "2023-01-01T20:00:00.000Z",
                        }
                    ],
                }
            ],
        }

        # Convert API response to match our model expectations
        processed_response: UserShowTestData = {
            "show": {
                "title": api_response["show"]["title"],  # type: ignore[index,misc] # Testing: Type validation
                "year": api_response["show"]["year"],  # type: ignore[index,misc] # Testing: Type validation
                "ids": {
                    k: str(v) if isinstance(v, int | str) else ""
                    for k, v in api_response["show"]["ids"].items()  # type: ignore[index,misc,union-attr] # Testing: Type validation
                },  # Convert to strings
                "overview": api_response["show"]["overview"],  # type: ignore[index,misc] # Testing: Type validation
            },
            "last_watched_at": api_response["last_watched_at"],
            "last_updated_at": api_response["last_updated_at"],
            "plays": api_response["plays"],
            "seasons": api_response["seasons"],
        }

        user_show = TraktUserShow(**processed_response)  # type: ignore[arg-type] # Testing: Type validation

        assert user_show.show.title == "Breaking Bad"
        assert user_show.show.year == 2008
        assert user_show.plays == 62
        assert user_show.seasons is not None
        assert len(user_show.seasons) == 1
        assert user_show.seasons[0]["number"] == 1

    def test_user_show_plays_validation(self):
        """Test plays field validation."""
        show_data: ShowTestData = {
            "title": "Test Show",
            "ids": {"trakt": "1"},
        }

        # Test negative plays (should be allowed as it's just an int)
        user_show = TraktUserShow(
            show=show_data,  # type: ignore[arg-type] # Testing: Type validation
            last_watched_at="2023-01-15T20:30:00Z",
            last_updated_at="2023-01-16T10:00:00Z",
            plays=0,  # Zero plays should be valid
        )
        assert user_show.plays == 0

        # Test large number of plays
        user_show = TraktUserShow(
            show=show_data,  # type: ignore[arg-type] # Testing: Type validation
            last_watched_at="2023-01-15T20:30:00Z",
            last_updated_at="2023-01-16T10:00:00Z",
            plays=999999,
        )
        assert user_show.plays == 999999

    def test_user_show_timestamp_formats(self):
        """Test various timestamp formats."""
        show_data: ShowTestData = {
            "title": "Test Show",
            "ids": {"trakt": "1"},
        }

        # Test with milliseconds
        user_show = TraktUserShow(
            show=show_data,  # type: ignore[arg-type] # Testing: Type validation
            last_watched_at="2023-01-15T20:30:00.123Z",
            last_updated_at="2023-01-16T10:00:00.456Z",
            plays=1,
        )
        assert user_show.last_watched_at == "2023-01-15T20:30:00.123Z"
        assert user_show.last_updated_at == "2023-01-16T10:00:00.456Z"

        # Test without milliseconds
        user_show = TraktUserShow(
            show=show_data,  # type: ignore[arg-type] # Testing: Type validation
            last_watched_at="2023-01-15T20:30:00Z",
            last_updated_at="2023-01-16T10:00:00Z",
            plays=1,
        )
        assert user_show.last_watched_at == "2023-01-15T20:30:00Z"
        assert user_show.last_updated_at == "2023-01-16T10:00:00Z"
