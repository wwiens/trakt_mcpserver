"""Tests for search endpoints module."""

from config.endpoints.search import SEARCH_ENDPOINTS


class TestSearchEndpoints:
    """Test search endpoints structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test SEARCH_ENDPOINTS is a dictionary."""
        assert isinstance(SEARCH_ENDPOINTS, dict)
        assert len(SEARCH_ENDPOINTS) > 0

    def test_search_endpoints_exist(self) -> None:
        """Test search endpoints are present."""
        assert "search" in SEARCH_ENDPOINTS
        assert SEARCH_ENDPOINTS["search"] == "/search"

    def test_search_endpoint_format(self) -> None:
        """Test search endpoint URL format."""
        assert SEARCH_ENDPOINTS["search"] == "/search"
        assert isinstance(SEARCH_ENDPOINTS["search"], str)
        assert SEARCH_ENDPOINTS["search"].startswith("/")

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in SEARCH_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in SEARCH_ENDPOINTS:
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
        for key, value in SEARCH_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in SEARCH_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
