"""Tests for movies endpoints module."""

from config.endpoints.movies import MOVIES_ENDPOINTS


class TestMoviesEndpoints:
    """Test movies endpoints structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test MOVIES_ENDPOINTS is a dictionary."""
        assert isinstance(MOVIES_ENDPOINTS, dict)
        assert len(MOVIES_ENDPOINTS) > 0

    def test_movie_endpoints_exist(self) -> None:
        """Test movie-related endpoints are present."""
        movie_endpoints = [
            "movies_trending",
            "movies_popular",
            "movies_favorited",
            "movies_played",
            "movies_watched",
        ]
        for endpoint in movie_endpoints:
            assert endpoint in MOVIES_ENDPOINTS
            assert isinstance(MOVIES_ENDPOINTS[endpoint], str)
            assert MOVIES_ENDPOINTS[endpoint].startswith("/")

    def test_rating_endpoints_exist(self) -> None:
        """Test movie rating endpoints are present."""
        assert "movie_ratings" in MOVIES_ENDPOINTS
        assert isinstance(MOVIES_ENDPOINTS["movie_ratings"], str)
        assert MOVIES_ENDPOINTS["movie_ratings"].startswith("/")

    def test_movie_endpoint_url_formats(self) -> None:
        """Test movie endpoint URL formats."""
        assert MOVIES_ENDPOINTS["movies_trending"] == "/movies/trending"
        assert MOVIES_ENDPOINTS["movies_popular"] == "/movies/popular"
        assert MOVIES_ENDPOINTS["movies_favorited"] == "/movies/favorited"
        assert MOVIES_ENDPOINTS["movies_played"] == "/movies/played"
        assert MOVIES_ENDPOINTS["movies_watched"] == "/movies/watched"

    def test_rating_endpoint_format(self) -> None:
        """Test movie rating endpoint format."""
        assert MOVIES_ENDPOINTS["movie_ratings"] == "/movies/:id/ratings"
        assert ":id" in MOVIES_ENDPOINTS["movie_ratings"]

    def test_endpoints_contain_movies(self) -> None:
        """Test all endpoints contain 'movie' in path."""
        for endpoint_key, endpoint_url in MOVIES_ENDPOINTS.items():
            assert "movie" in endpoint_url, (
                f"Movie endpoint {endpoint_key} should contain 'movie'"
            )

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in MOVIES_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in MOVIES_ENDPOINTS:
            # Should use lowercase and underscores
            assert key.islower(), f"Endpoint key {key} should be lowercase"
            assert " " not in key, f"Endpoint key {key} should not contain spaces"
            # Should not start or end with underscore
            assert not key.startswith("_"), (
                f"Endpoint key {key} should not start with underscore"
            )
            assert not key.endswith("_"), (
                f"Endpoint key {key} should not end with underscore"
            )

    def test_all_values_are_strings(self) -> None:
        """Test all endpoint values are strings."""
        for key, value in MOVIES_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in MOVIES_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
