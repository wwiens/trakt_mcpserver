"""Tests for auth endpoints module."""

from config.endpoints.auth import AUTH_ENDPOINTS


class TestAuthEndpoints:
    """Test authentication endpoints structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test AUTH_ENDPOINTS is a dictionary."""
        assert isinstance(AUTH_ENDPOINTS, dict)
        assert len(AUTH_ENDPOINTS) > 0

    def test_auth_endpoints_exist(self) -> None:
        """Test authentication endpoints are present."""
        auth_endpoints = ["device_code", "device_token", "revoke"]
        for endpoint in auth_endpoints:
            assert endpoint in AUTH_ENDPOINTS
            assert isinstance(AUTH_ENDPOINTS[endpoint], str)
            assert AUTH_ENDPOINTS[endpoint].startswith("/")

    def test_auth_endpoint_formats(self) -> None:
        """Test authentication endpoint URL formats."""
        assert AUTH_ENDPOINTS["device_code"] == "/oauth/device/code"
        assert AUTH_ENDPOINTS["device_token"] == "/oauth/device/token"
        assert AUTH_ENDPOINTS["revoke"] == "/oauth/revoke"

    def test_oauth_endpoints_contain_oauth(self) -> None:
        """Test OAuth endpoints contain 'oauth' in path."""
        for endpoint_key, endpoint_url in AUTH_ENDPOINTS.items():
            assert "oauth" in endpoint_url, (
                f"Auth endpoint {endpoint_key} should contain 'oauth'"
            )

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in AUTH_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in AUTH_ENDPOINTS:
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
        for key, value in AUTH_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in AUTH_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
