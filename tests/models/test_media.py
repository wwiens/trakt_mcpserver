"""Tests for the models.media module."""

from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from models.movies import TraktMovie, TraktPopularMovie, TraktTrendingMovie
from models.shows import TraktEpisode, TraktPopularShow, TraktShow, TraktTrendingShow

if TYPE_CHECKING:
    from tests.models.test_data_types import (
        EpisodeTestData,
        MovieTestData,
        ShowTestData,
    )


class TestTraktShow:
    """Tests for the TraktShow model."""

    def test_valid_show_creation(self):
        """Test creating a valid TraktShow instance."""
        show_data: ShowTestData = {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {
                "trakt": "1",
                "slug": "breaking-bad",
                "tvdb": "81189",
                "imdb": "tt0903747",
                "tmdb": "1396",
            },
            "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
        }

        show = TraktShow(**show_data)

        assert show.title == "Breaking Bad"
        assert show.year == 2008
        assert show.ids == show_data["ids"]
        assert (
            show.overview
            == "A high school chemistry teacher diagnosed with inoperable lung cancer."
        )

    def test_show_minimal_data(self):
        """Test creating show with minimal required data."""
        minimal_data: ShowTestData = {
            "title": "Test Show",
            "year": 2020,
            "ids": {"trakt": "123"},
        }

        show = TraktShow(**minimal_data)

        assert show.title == "Test Show"
        assert show.year == 2020
        assert show.ids == {"trakt": "123"}
        assert show.overview is None

    def test_show_missing_title(self):
        """Test that title is required."""
        with pytest.raises(ValidationError) as exc_info:
            TraktShow(ids={"trakt": "123"})  # type: ignore[call-arg] # Testing: Missing required 'title' field

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    def test_show_missing_ids(self):
        """Test that ids field is required."""
        with pytest.raises(ValidationError) as exc_info:
            TraktShow(title="Test Show")  # type: ignore[call-arg] # Testing: Missing required 'ids' field

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("ids",) for error in errors)

    def test_show_field_types(self):
        """Test that fields have correct types."""
        # Test with clearly incompatible title type
        with pytest.raises(ValidationError):
            TraktShow(title=["not", "a", "string"], ids={"trakt": "123"})  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types

        # Test with clearly incompatible year type
        with pytest.raises(ValidationError):
            TraktShow(title="Test", year=["not", "an", "int"], ids={"trakt": "123"})  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types

        # Test with wrong ids type
        with pytest.raises(ValidationError):
            TraktShow(title="Test", ids="not_a_dict")  # type: ignore[arg-type] # Testing: String where dict expected for 'ids'

    def test_show_serialization(self):
        """Test that TraktShow can be serialized."""
        show_data: ShowTestData = {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": "1", "slug": "breaking-bad"},
            "overview": "Great show",
        }

        show = TraktShow(**show_data)
        serialized = show.model_dump()

        assert serialized == show_data

    def test_show_with_none_values(self):
        """Test show with explicit None values."""
        show_data: ShowTestData = {
            "title": "Test Show",
            "year": 2021,
            "ids": {"trakt": "123"},
            "overview": None,
        }

        show = TraktShow(**show_data)

        assert show.title == "Test Show"
        assert show.year == 2021
        assert show.overview is None


class TestTraktMovie:
    """Tests for the TraktMovie model."""

    def test_valid_movie_creation(self):
        """Test creating a valid TraktMovie instance."""
        movie_data: MovieTestData = {
            "title": "Inception",
            "year": 2010,
            "ids": {
                "trakt": "1",
                "slug": "inception-2010",
                "imdb": "tt1375666",
                "tmdb": "27205",
            },
            "overview": "A thief who steals corporate secrets through dream-sharing technology.",
        }

        movie = TraktMovie(**movie_data)

        assert movie.title == "Inception"
        assert movie.year == 2010
        assert movie.ids == movie_data["ids"]
        assert (
            movie.overview
            == "A thief who steals corporate secrets through dream-sharing technology."
        )

    def test_movie_minimal_data(self):
        """Test creating movie with minimal required data."""
        minimal_data: MovieTestData = {
            "title": "Test Movie",
            "year": 2019,
            "ids": {"trakt": "456"},
        }

        movie = TraktMovie(**minimal_data)

        assert movie.title == "Test Movie"
        assert movie.year == 2019
        assert movie.ids == {"trakt": "456"}
        assert movie.overview is None

    def test_movie_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktMovie()  # type: ignore[call-arg] # Testing: All required fields missing

        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}
        assert "title" in required_fields
        assert "ids" in required_fields

    def test_movie_field_types(self):
        """Test that fields have correct types."""
        # Test with clearly incompatible types
        with pytest.raises(ValidationError):
            TraktMovie(title=["not", "a", "string"], ids={"trakt": "123"})  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types

        with pytest.raises(ValidationError):
            TraktMovie(title="Test", year=["not", "an", "int"], ids={"trakt": "123"})  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types

    def test_movie_serialization(self):
        """Test that TraktMovie can be serialized."""
        movie_data: MovieTestData = {
            "title": "Inception",
            "year": 2010,
            "ids": {"trakt": "1"},
            "overview": "Great movie",
        }

        movie = TraktMovie(**movie_data)
        serialized = movie.model_dump()

        assert serialized == movie_data


class TestTraktEpisode:
    """Tests for the TraktEpisode model."""

    def test_valid_episode_creation(self):
        """Test creating a valid TraktEpisode instance."""
        episode_data: EpisodeTestData = {
            "season": 1,
            "number": 1,
            "title": "Pilot",
            "ids": {"trakt": "123", "tvdb": "456"},
            "last_watched_at": "2023-01-15T20:30:00Z",
        }

        episode = TraktEpisode(**episode_data)

        assert episode.season == 1
        assert episode.number == 1
        assert episode.title == "Pilot"
        assert episode.ids == {"trakt": "123", "tvdb": "456"}
        assert episode.last_watched_at == "2023-01-15T20:30:00Z"

    def test_episode_minimal_data(self):
        """Test creating episode with minimal required data."""
        minimal_data = {
            "season": 2,
            "number": 5,
        }

        episode = TraktEpisode(**minimal_data)  # type: ignore[arg-type] # Testing: Minimal valid data without TypedDict

        assert episode.season == 2
        assert episode.number == 5
        assert episode.title is None
        assert episode.ids is None
        assert episode.last_watched_at is None

    def test_episode_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktEpisode()  # type: ignore[call-arg] # Testing: All required fields missing

        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}
        assert "season" in required_fields
        assert "number" in required_fields

    def test_episode_field_types(self):
        """Test that fields have correct types."""
        # Test with clearly incompatible types
        with pytest.raises(ValidationError):
            TraktEpisode(season=["not", "an", "int"], number=1)  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types

        with pytest.raises(ValidationError):
            TraktEpisode(season=1, number=["not", "an", "int"])  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types

    def test_episode_serialization(self):
        """Test that TraktEpisode can be serialized."""
        episode_data = {
            "season": 1,
            "number": 1,
            "title": "Pilot",
            "ids": {"trakt": "123"},
            "last_watched_at": "2023-01-15T20:30:00Z",
        }

        episode = TraktEpisode(**episode_data)  # type: ignore[arg-type] # Testing: Valid episode data without TypedDict
        serialized = episode.model_dump()

        assert serialized == episode_data


class TestTraktTrendingShow:
    """Tests for the TraktTrendingShow model."""

    def test_valid_trending_show_creation(self):
        """Test creating a valid TraktTrendingShow instance."""
        trending_data = {
            "watchers": 150,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": "1"},
                "overview": "Great show",
            },
        }

        trending_show = TraktTrendingShow(**trending_data)  # type: ignore[arg-type] # Testing: Dict where TraktShow expected

        assert trending_show.watchers == 150
        assert trending_show.show.title == "Breaking Bad"
        assert trending_show.show.year == 2008

    def test_trending_show_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktTrendingShow()  # type: ignore[call-arg] # Testing: All required fields missing

        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}
        assert "watchers" in required_fields
        assert "show" in required_fields

    def test_trending_show_nested_validation(self):
        """Test that nested show validation works."""
        # Missing required show fields
        with pytest.raises(ValidationError):
            TraktTrendingShow(  # type: ignore[arg-type] # Testing: Incomplete show data missing 'ids'
                watchers=150,
                show={"title": "Test"},  # type: ignore[arg-type] # Testing: Incomplete show data missing 'ids'
            )

    def test_trending_show_serialization(self):
        """Test that TraktTrendingShow can be serialized."""
        trending_data = {
            "watchers": 150,
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": "1"},
                "overview": "Great show",
            },
        }

        trending_show = TraktTrendingShow(**trending_data)  # type: ignore[arg-type] # Testing: Dict where TraktShow expected
        serialized = trending_show.model_dump()

        assert serialized == trending_data


class TestTraktTrendingMovie:
    """Tests for the TraktTrendingMovie model."""

    def test_valid_trending_movie_creation(self):
        """Test creating a valid TraktTrendingMovie instance."""
        trending_data = {
            "watchers": 200,
            "movie": {
                "title": "Inception",
                "year": 2010,
                "ids": {"trakt": "1"},
                "overview": "Great movie",
            },
        }

        trending_movie = TraktTrendingMovie(**trending_data)  # type: ignore[arg-type] # Testing: Dict where TraktMovie expected

        assert trending_movie.watchers == 200
        assert trending_movie.movie.title == "Inception"
        assert trending_movie.movie.year == 2010

    def test_trending_movie_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktTrendingMovie()  # type: ignore[call-arg] # Testing: All required fields missing

        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}
        assert "watchers" in required_fields
        assert "movie" in required_fields

    def test_trending_movie_nested_validation(self):
        """Test that nested movie validation works."""
        # Missing required movie fields
        with pytest.raises(ValidationError):
            TraktTrendingMovie(  # type: ignore[arg-type] # Testing: Incomplete movie data missing 'ids'
                watchers=200,
                movie={"title": "Test"},  # type: ignore[arg-type] # Testing: Incomplete movie data missing 'ids'
            )


class TestTraktPopularShow:
    """Tests for the TraktPopularShow model."""

    def test_valid_popular_show_creation(self):
        """Test creating a valid TraktPopularShow instance."""
        popular_data = {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": "1"},
                "overview": "Great show",
            }
        }

        popular_show = TraktPopularShow(**popular_data)  # type: ignore[arg-type] # Testing: Dict where TraktShow expected

        assert popular_show.show.title == "Breaking Bad"
        assert popular_show.show.year == 2008

    def test_popular_show_from_api_response(self):
        """Test creating popular show from API response format."""
        # Simulate API response format where show data is at root level
        api_data = {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {"trakt": "1"},
            "overview": "Great show",
        }

        popular_show = TraktPopularShow.from_api_response(api_data)

        assert popular_show.show.title == "Breaking Bad"
        assert popular_show.show.year == 2008
        assert popular_show.show.ids == {"trakt": "1"}

    def test_popular_show_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktPopularShow()  # type: ignore[call-arg] # Testing: Missing required 'show' field

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("show",) for error in errors)

    def test_popular_show_serialization(self):
        """Test that TraktPopularShow can be serialized."""
        popular_data = {
            "show": {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": "1"},
                "overview": "Great show",
            }
        }

        popular_show = TraktPopularShow(**popular_data)  # type: ignore[arg-type] # Testing: Dict where TraktShow expected
        serialized = popular_show.model_dump()

        assert serialized == popular_data


class TestTraktPopularMovie:
    """Tests for the TraktPopularMovie model."""

    def test_valid_popular_movie_creation(self):
        """Test creating a valid TraktPopularMovie instance."""
        popular_data = {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "ids": {"trakt": "1"},
                "overview": "Great movie",
            }
        }

        popular_movie = TraktPopularMovie(**popular_data)  # type: ignore[arg-type] # Testing: Dict where TraktMovie expected

        assert popular_movie.movie.title == "Inception"
        assert popular_movie.movie.year == 2010

    def test_popular_movie_from_api_response(self):
        """Test creating popular movie from API response format."""
        # Simulate API response format where movie data is at root level
        api_data = {
            "title": "Inception",
            "year": 2010,
            "ids": {"trakt": "1"},
            "overview": "Great movie",
        }

        popular_movie = TraktPopularMovie.from_api_response(api_data)

        assert popular_movie.movie.title == "Inception"
        assert popular_movie.movie.year == 2010
        assert popular_movie.movie.ids == {"trakt": "1"}

    def test_popular_movie_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktPopularMovie()  # type: ignore[call-arg] # Testing: Missing required 'movie' field

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("movie",) for error in errors)

    def test_popular_movie_serialization(self):
        """Test that TraktPopularMovie can be serialized."""
        popular_data = {
            "movie": {
                "title": "Inception",
                "year": 2010,
                "ids": {"trakt": "1"},
                "overview": "Great movie",
            }
        }

        popular_movie = TraktPopularMovie(**popular_data)  # type: ignore[arg-type] # Testing: Dict where TraktMovie expected
        serialized = popular_movie.model_dump()

        assert serialized == popular_data


class TestMediaModelIntegration:
    """Integration tests for media models working together."""

    def test_complex_show_data_structure(self):
        """Test complex show data structure with all fields."""
        complex_show_data = {
            "title": "Game of Thrones",
            "year": 2011,
            "ids": {
                "trakt": "1390",
                "slug": "game-of-thrones",
                "tvdb": "121361",
                "imdb": "tt0944947",
                "tmdb": "1399",
            },
            "overview": "Seven noble families fight for control of the mythical land of Westeros.",
        }

        # Test direct show creation
        show = TraktShow(**complex_show_data)  # type: ignore[arg-type] # Testing: Valid show data without TypedDict
        assert show.title == "Game of Thrones"

        # Test in trending context
        trending_show = TraktTrendingShow(watchers=5000, show=complex_show_data)  # type: ignore[arg-type] # Testing: Dict where TraktShow expected
        assert trending_show.watchers == 5000
        assert trending_show.show.title == "Game of Thrones"

        # Test in popular context
        popular_show = TraktPopularShow(show=complex_show_data)  # type: ignore[arg-type] # Testing: Dict where TraktShow expected
        assert popular_show.show.title == "Game of Thrones"

    def test_complex_movie_data_structure(self):
        """Test complex movie data structure with all fields."""
        complex_movie_data = {
            "title": "The Dark Knight",
            "year": 2008,
            "ids": {
                "trakt": "1",
                "slug": "the-dark-knight-2008",
                "imdb": "tt0468569",
                "tmdb": "155",
            },
            "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham.",
        }

        # Test direct movie creation
        movie = TraktMovie(**complex_movie_data)  # type: ignore[arg-type] # Testing: Valid movie data without TypedDict
        assert movie.title == "The Dark Knight"

        # Test in trending context
        trending_movie = TraktTrendingMovie(watchers=3000, movie=complex_movie_data)  # type: ignore[arg-type] # Testing: Dict where TraktMovie expected
        assert trending_movie.watchers == 3000
        assert trending_movie.movie.title == "The Dark Knight"

        # Test in popular context
        popular_movie = TraktPopularMovie(movie=complex_movie_data)  # type: ignore[arg-type] # Testing: Dict where TraktMovie expected
        assert popular_movie.movie.title == "The Dark Knight"

    def test_episode_integration(self):
        """Test episode model integration scenarios."""
        episode_data = {
            "season": 1,
            "number": 1,
            "title": "Winter Is Coming",
            "ids": {
                "trakt": "73640",
                "tvdb": "349232",
                "imdb": "tt1596220",
                "tmdb": "63056",
            },
            "last_watched_at": "2023-12-01T21:00:00Z",
        }

        episode = TraktEpisode(**episode_data)  # type: ignore[arg-type] # Testing: Valid episode data without TypedDict

        assert episode.season == 1
        assert episode.number == 1
        assert episode.title == "Winter Is Coming"
        assert episode.ids is not None and "trakt" in episode.ids
        assert episode.last_watched_at == "2023-12-01T21:00:00Z"

        # Test serialization round-trip
        serialized = episode.model_dump()
        reconstructed = TraktEpisode(**serialized)
        assert reconstructed.season == episode.season
        assert reconstructed.number == episode.number
        assert reconstructed.title == episode.title
