"""Tests for lists endpoints module."""

from typing import TYPE_CHECKING

from config.endpoints.lists import LISTS_ENDPOINTS

if TYPE_CHECKING:
    from config.endpoints import EndpointKey


class TestListsEndpoints:
    """Test lists endpoints structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test LISTS_ENDPOINTS is a dictionary."""
        assert isinstance(LISTS_ENDPOINTS, dict)
        assert len(LISTS_ENDPOINTS) > 0

    def test_list_endpoints_exist(self) -> None:
        """Test list-related endpoints are present."""
        list_endpoints: list[EndpointKey] = [
            "list_items",
            "trending_lists",
            "popular_lists",
        ]
        for endpoint in list_endpoints:
            assert endpoint in LISTS_ENDPOINTS
            assert isinstance(LISTS_ENDPOINTS[endpoint], str)
            assert LISTS_ENDPOINTS[endpoint].startswith("/")

    def test_list_endpoint_url_formats(self) -> None:
        """Test list endpoint URL formats."""
        assert LISTS_ENDPOINTS["list_items"] == "/users/:owner/lists/:id/items/:type"
        assert LISTS_ENDPOINTS["trending_lists"] == "/lists/trending"
        assert LISTS_ENDPOINTS["popular_lists"] == "/lists/popular"

    def test_list_items_endpoint_placeholders(self) -> None:
        """Test the list items endpoint carries the expected placeholders."""
        endpoint = LISTS_ENDPOINTS["list_items"]
        for param in (":owner", ":id", ":type"):
            assert param in endpoint, f"Parameter {param} not found in list_items"

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in LISTS_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in LISTS_ENDPOINTS:
            assert key.islower(), f"Endpoint key {key} should be lowercase"
            assert " " not in key, f"Endpoint key {key} should not contain spaces"
            assert not key.startswith("_"), (
                f"Endpoint key {key} should not start with underscore"
            )
            assert not key.endswith("_"), (
                f"Endpoint key {key} should not end with underscore"
            )

    def test_all_values_are_strings(self) -> None:
        """Test all endpoint values are strings."""
        for key, value in LISTS_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in LISTS_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
