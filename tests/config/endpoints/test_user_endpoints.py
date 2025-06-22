"""Tests for user endpoints module."""

from config.endpoints.user import USER_ENDPOINTS


class TestUserEndpoints:
    """Test user endpoints structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test USER_ENDPOINTS is a dictionary."""
        assert isinstance(USER_ENDPOINTS, dict)
        assert len(USER_ENDPOINTS) > 0

    def test_user_endpoints_exist(self) -> None:
        """Test user endpoints are present."""
        user_endpoints = [
            "user_watched_shows",
            "user_watched_movies",
        ]
        for endpoint in user_endpoints:
            assert endpoint in USER_ENDPOINTS
            assert isinstance(USER_ENDPOINTS[endpoint], str)
            assert USER_ENDPOINTS[endpoint].startswith("/")

    def test_user_endpoint_url_formats(self) -> None:
        """Test user endpoint URL formats."""
        assert USER_ENDPOINTS["user_watched_shows"] == "/sync/watched/shows"
        assert USER_ENDPOINTS["user_watched_movies"] == "/sync/watched/movies"

    def test_sync_endpoints_contain_sync(self) -> None:
        """Test sync endpoints contain 'sync' in path."""
        for endpoint_key, endpoint_url in USER_ENDPOINTS.items():
            assert "sync" in endpoint_url, (
                f"User endpoint {endpoint_key} should contain 'sync'"
            )

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in USER_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in USER_ENDPOINTS:
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
        for key, value in USER_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in USER_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
