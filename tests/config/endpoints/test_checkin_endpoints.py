"""Tests for checkin endpoints module."""

from config.endpoints.checkin import CHECKIN_ENDPOINTS


class TestCheckinEndpoints:
    """Test checkin endpoints structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test CHECKIN_ENDPOINTS is a dictionary."""
        assert isinstance(CHECKIN_ENDPOINTS, dict)
        assert len(CHECKIN_ENDPOINTS) > 0

    def test_checkin_endpoints_exist(self) -> None:
        """Test check-in endpoints are present."""
        assert "checkin" in CHECKIN_ENDPOINTS
        assert CHECKIN_ENDPOINTS["checkin"] == "/checkin"

    def test_checkin_endpoint_format(self) -> None:
        """Test checkin endpoint URL format."""
        assert CHECKIN_ENDPOINTS["checkin"] == "/checkin"
        assert isinstance(CHECKIN_ENDPOINTS["checkin"], str)
        assert CHECKIN_ENDPOINTS["checkin"].startswith("/")

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in CHECKIN_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in CHECKIN_ENDPOINTS:
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
        for key, value in CHECKIN_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in CHECKIN_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
