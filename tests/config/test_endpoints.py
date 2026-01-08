"""Integration tests for config endpoints direct imports."""

# Test imports from domain-specific config modules
from config.endpoints import TRAKT_ENDPOINTS


class TestTraktEndpoints:
    """Test TRAKT_ENDPOINTS dictionary structure and contents."""

    def test_endpoints_is_dict(self) -> None:
        """Test TRAKT_ENDPOINTS is a dictionary."""
        assert isinstance(TRAKT_ENDPOINTS, dict)
        assert len(TRAKT_ENDPOINTS) > 0

    def test_auth_endpoints_exist(self) -> None:
        """Test authentication endpoints are present."""
        auth_endpoints = ["device_code", "device_token", "revoke"]
        for endpoint in auth_endpoints:
            assert endpoint in TRAKT_ENDPOINTS
            assert isinstance(TRAKT_ENDPOINTS[endpoint], str)
            assert TRAKT_ENDPOINTS[endpoint].startswith("/")

    def test_show_endpoints_exist(self) -> None:
        """Test show-related endpoints are present."""
        show_endpoints = [
            "shows_trending",
            "shows_popular",
            "shows_favorited",
            "shows_played",
            "shows_watched",
            "user_watched_shows",
        ]
        for endpoint in show_endpoints:
            assert endpoint in TRAKT_ENDPOINTS
            assert isinstance(TRAKT_ENDPOINTS[endpoint], str)
            assert TRAKT_ENDPOINTS[endpoint].startswith("/")

    def test_movie_endpoints_exist(self) -> None:
        """Test movie-related endpoints are present."""
        movie_endpoints = [
            "movies_trending",
            "movies_popular",
            "movies_favorited",
            "movies_played",
            "movies_watched",
            "user_watched_movies",
        ]
        for endpoint in movie_endpoints:
            assert endpoint in TRAKT_ENDPOINTS
            assert isinstance(TRAKT_ENDPOINTS[endpoint], str)
            assert TRAKT_ENDPOINTS[endpoint].startswith("/")

    def test_search_endpoints_exist(self) -> None:
        """Test search endpoints are present."""
        assert "search" in TRAKT_ENDPOINTS
        assert TRAKT_ENDPOINTS["search"] == "/search"

    def test_checkin_endpoints_exist(self) -> None:
        """Test check-in endpoints are present."""
        assert "checkin" in TRAKT_ENDPOINTS
        assert TRAKT_ENDPOINTS["checkin"] == "/checkin"

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
            assert endpoint in TRAKT_ENDPOINTS
            assert isinstance(TRAKT_ENDPOINTS[endpoint], str)
            assert TRAKT_ENDPOINTS[endpoint].startswith("/")

    def test_rating_endpoints_exist(self) -> None:
        """Test rating endpoints are present."""
        rating_endpoints = ["show_ratings", "movie_ratings"]
        for endpoint in rating_endpoints:
            assert endpoint in TRAKT_ENDPOINTS
            assert isinstance(TRAKT_ENDPOINTS[endpoint], str)
            assert TRAKT_ENDPOINTS[endpoint].startswith("/")

    def test_recommendation_endpoints_exist(self) -> None:
        """Test recommendation endpoints are present."""
        recommendation_endpoints = [
            "recommendations_movies",
            "recommendations_shows",
            "hide_movie_recommendation",
            "hide_show_recommendation",
            "unhide_recommendations",
        ]
        for endpoint in recommendation_endpoints:
            assert endpoint in TRAKT_ENDPOINTS
            assert isinstance(TRAKT_ENDPOINTS[endpoint], str)
            assert TRAKT_ENDPOINTS[endpoint].startswith("/")


class TestEndpointUrlFormats:
    """Test endpoint URL formats and structure."""

    def test_all_endpoints_start_with_slash(self) -> None:
        """Test all endpoints start with forward slash."""
        for endpoint_key, endpoint_url in TRAKT_ENDPOINTS.items():
            assert endpoint_url.startswith("/"), (
                f"Endpoint {endpoint_key} should start with '/'"
            )

    def test_auth_endpoint_formats(self) -> None:
        """Test authentication endpoint URL formats."""
        assert TRAKT_ENDPOINTS["device_code"] == "/oauth/device/code"
        assert TRAKT_ENDPOINTS["device_token"] == "/oauth/device/token"
        assert TRAKT_ENDPOINTS["revoke"] == "/oauth/revoke"

    def test_oauth_endpoints_contain_oauth(self) -> None:
        """Test OAuth endpoints contain 'oauth' in path."""
        oauth_endpoints = ["device_code", "device_token", "revoke"]
        for endpoint in oauth_endpoints:
            assert "oauth" in TRAKT_ENDPOINTS[endpoint]

    def test_sync_endpoints_contain_sync(self) -> None:
        """Test sync endpoints contain 'sync' in path."""
        sync_endpoints = ["user_watched_shows", "user_watched_movies"]
        for endpoint in sync_endpoints:
            assert "sync" in TRAKT_ENDPOINTS[endpoint]

    def test_parameterized_endpoints_contain_placeholders(self) -> None:
        """Test parameterized endpoints contain proper placeholders."""
        parameterized_endpoints = {
            "comments_movie": [":id", ":sort"],
            "comments_show": [":id", ":sort"],
            "comments_season": [":id", ":season", ":sort"],
            "comments_episode": [":id", ":season", ":episode", ":sort"],
            "comment": [":id"],
            "comment_replies": [":id"],
            "show_ratings": [":id"],
            "movie_ratings": [":id"],
            "hide_movie_recommendation": [":id"],
            "hide_show_recommendation": [":id"],
        }

        for endpoint_key, expected_params in parameterized_endpoints.items():
            endpoint_url = TRAKT_ENDPOINTS[endpoint_key]
            for param in expected_params:
                assert param in endpoint_url, (
                    f"Parameter {param} not found in {endpoint_key}"
                )

    def test_endpoint_categories_consistency(self) -> None:
        """Test endpoint naming follows consistent patterns."""
        # Show endpoints should start with 'shows_' or contain 'shows'
        show_keys = [k for k in TRAKT_ENDPOINTS if "show" in k]
        for key in show_keys:
            url = TRAKT_ENDPOINTS[key]
            assert "show" in url or "sync" in url, (
                f"Show endpoint {key} should contain 'show' or 'sync'"
            )

        # Movie endpoints should start with 'movies_' or contain 'movies'
        movie_keys = [k for k in TRAKT_ENDPOINTS if "movie" in k]
        for key in movie_keys:
            url = TRAKT_ENDPOINTS[key]
            assert "movie" in url or "sync" in url, (
                f"Movie endpoint {key} should contain 'movie' or 'sync'"
            )

    def test_combined_endpoints_match_domain_modules(self) -> None:
        """Test that combined TRAKT_ENDPOINTS matches domain-specific endpoint modules."""
        # Import from domain-specific modules
        from config.endpoints.auth import AUTH_ENDPOINTS
        from config.endpoints.checkin import CHECKIN_ENDPOINTS
        from config.endpoints.comments import COMMENTS_ENDPOINTS
        from config.endpoints.movies import MOVIES_ENDPOINTS
        from config.endpoints.recommendations import RECOMMENDATIONS_ENDPOINTS
        from config.endpoints.search import SEARCH_ENDPOINTS
        from config.endpoints.shows import SHOWS_ENDPOINTS
        from config.endpoints.user import USER_ENDPOINTS

        # All domain endpoints should be present in combined TRAKT_ENDPOINTS
        all_domain_endpoints = {
            **AUTH_ENDPOINTS,
            **SHOWS_ENDPOINTS,
            **MOVIES_ENDPOINTS,
            **RECOMMENDATIONS_ENDPOINTS,
            **COMMENTS_ENDPOINTS,
            **SEARCH_ENDPOINTS,
            **CHECKIN_ENDPOINTS,
            **USER_ENDPOINTS,
        }

        # TRAKT_ENDPOINTS should contain all domain endpoints
        for key, value in all_domain_endpoints.items():
            assert key in TRAKT_ENDPOINTS, (
                f"Domain endpoint {key} missing from TRAKT_ENDPOINTS"
            )
            assert TRAKT_ENDPOINTS[key] == value, (
                f"Domain endpoint {key} value mismatch"
            )

        # TRAKT_ENDPOINTS should not contain extra endpoints
        for key in TRAKT_ENDPOINTS:
            assert key in all_domain_endpoints, (
                f"Unexpected endpoint {key} in TRAKT_ENDPOINTS"
            )


class TestEndpointsIntegration:
    """Test integration aspects of endpoints configuration."""

    def test_no_duplicate_urls(self) -> None:
        """Test there are no duplicate endpoint URLs."""
        urls = list(TRAKT_ENDPOINTS.values())
        unique_urls = set(urls)
        # Allow some duplicates for aliases, but check major ones are unique
        assert len(unique_urls) >= len(urls) * 0.8  # At least 80% should be unique

    def test_endpoint_naming_conventions(self) -> None:
        """Test endpoint keys follow consistent naming conventions."""
        for key in TRAKT_ENDPOINTS:
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
        for key, value in TRAKT_ENDPOINTS.items():
            assert isinstance(value, str), (
                f"Endpoint {key} value should be string, got {type(value)}"
            )

    def test_no_empty_endpoints(self) -> None:
        """Test no endpoint URLs are empty."""
        for key, value in TRAKT_ENDPOINTS.items():
            assert value, f"Endpoint {key} should not be empty"
            assert len(value) > 1, f"Endpoint {key} should be more than just '/'"
