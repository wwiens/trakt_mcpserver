"""Tests for shows endpoints module."""

from config.endpoints.shows import SHOWS_ENDPOINTS


class TestShowsEndpoints:
    """Test shows endpoints structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test SHOWS_ENDPOINTS is a dictionary."""
        assert isinstance(SHOWS_ENDPOINTS, dict)
        assert len(SHOWS_ENDPOINTS) > 0

    def test_show_endpoints_exist(self) -> None:
        """Test show-related endpoints are present."""
        show_endpoints = [
            "shows_trending",
            "shows_popular",
            "shows_favorited",
            "shows_played",
            "shows_watched",
        ]
        for endpoint in show_endpoints:
            assert endpoint in SHOWS_ENDPOINTS
            assert isinstance(SHOWS_ENDPOINTS[endpoint], str)
            assert SHOWS_ENDPOINTS[endpoint].startswith("/")

    def test_rating_endpoints_exist(self) -> None:
        """Test show rating endpoints are present."""
        assert "show_ratings" in SHOWS_ENDPOINTS
        assert isinstance(SHOWS_ENDPOINTS["show_ratings"], str)
        assert SHOWS_ENDPOINTS["show_ratings"].startswith("/")

    def test_show_endpoint_url_formats(self) -> None:
        """Test show endpoint URL formats."""
        assert SHOWS_ENDPOINTS["shows_trending"] == "/shows/trending"
        assert SHOWS_ENDPOINTS["shows_popular"] == "/shows/popular"
        assert SHOWS_ENDPOINTS["shows_favorited"] == "/shows/favorited"
        assert SHOWS_ENDPOINTS["shows_played"] == "/shows/played"
        assert SHOWS_ENDPOINTS["shows_watched"] == "/shows/watched"

    def test_rating_endpoint_format(self) -> None:
        """Test show rating endpoint format."""
        assert SHOWS_ENDPOINTS["show_ratings"] == "/shows/:id/ratings"
        assert ":id" in SHOWS_ENDPOINTS["show_ratings"]

    def test_endpoints_contain_shows(self) -> None:
        """Test all endpoints contain 'shows' in path."""
        for endpoint_key, endpoint_url in SHOWS_ENDPOINTS.items():
            assert "show" in endpoint_url, (
                f"Show endpoint {endpoint_key} should contain 'show'"
            )

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in SHOWS_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in SHOWS_ENDPOINTS:
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
        for key, value in SHOWS_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in SHOWS_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
