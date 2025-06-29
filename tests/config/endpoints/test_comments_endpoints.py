"""Tests for comments endpoints module."""

from config.endpoints.comments import COMMENTS_ENDPOINTS


class TestCommentsEndpoints:
    """Test comments endpoints structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test COMMENTS_ENDPOINTS is a dictionary."""
        assert isinstance(COMMENTS_ENDPOINTS, dict)
        assert len(COMMENTS_ENDPOINTS) > 0

    def test_comment_endpoints_exist(self) -> None:
        """Test comment-related endpoints are present."""
        comment_endpoints = [
            "comments_movie",
            "comments_show",
            "comments_season",
            "comments_episode",
            "comment",
            "comment_replies",
        ]
        for endpoint in comment_endpoints:
            assert endpoint in COMMENTS_ENDPOINTS
            assert isinstance(COMMENTS_ENDPOINTS[endpoint], str)
            assert COMMENTS_ENDPOINTS[endpoint].startswith("/")

    def test_comment_endpoint_url_formats(self) -> None:
        """Test comment endpoint URL formats."""
        assert COMMENTS_ENDPOINTS["comments_movie"] == "/movies/:id/comments/:sort"
        assert COMMENTS_ENDPOINTS["comments_show"] == "/shows/:id/comments/:sort"
        assert (
            COMMENTS_ENDPOINTS["comments_season"]
            == "/shows/:id/seasons/:season/comments/:sort"
        )
        assert (
            COMMENTS_ENDPOINTS["comments_episode"]
            == "/shows/:id/seasons/:season/episodes/:episode/comments/:sort"
        )
        assert COMMENTS_ENDPOINTS["comment"] == "/comments/:id"
        assert COMMENTS_ENDPOINTS["comment_replies"] == "/comments/:id/replies/:sort"

    def test_parameterized_endpoints_contain_placeholders(self) -> None:
        """Test parameterized endpoints contain proper placeholders."""
        parameterized_endpoints = {
            "comments_movie": [":id", ":sort"],
            "comments_show": [":id", ":sort"],
            "comments_season": [":id", ":season", ":sort"],
            "comments_episode": [":id", ":season", ":episode", ":sort"],
            "comment": [":id"],
            "comment_replies": [":id", ":sort"],
        }

        for endpoint_key, expected_params in parameterized_endpoints.items():
            endpoint_url = COMMENTS_ENDPOINTS[endpoint_key]
            for param in expected_params:
                assert param in endpoint_url, (
                    f"Parameter {param} not found in {endpoint_key}"
                )

    def test_endpoints_contain_comments(self) -> None:
        """Test comment endpoints contain 'comment' in path."""
        for endpoint_key, endpoint_url in COMMENTS_ENDPOINTS.items():
            assert "comment" in endpoint_url, (
                f"Comment endpoint {endpoint_key} should contain 'comment'"
            )

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in COMMENTS_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in COMMENTS_ENDPOINTS:
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
        for key, value in COMMENTS_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in COMMENTS_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
