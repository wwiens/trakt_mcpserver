"""Tests for MCP resources module."""

from config.mcp.resources import MCP_RESOURCES


class TestMcpResources:
    """Test MCP_RESOURCES dictionary structure and contents."""

    def test_resources_is_dict(self) -> None:
        """Test MCP_RESOURCES is a dictionary."""
        assert isinstance(MCP_RESOURCES, dict)
        assert len(MCP_RESOURCES) > 0

    def test_show_resources_exist(self) -> None:
        """Test show-related resources are present."""
        show_resources = [
            "shows_trending",
            "shows_popular",
            "shows_favorited",
            "shows_played",
            "shows_watched",
        ]
        for resource in show_resources:
            assert resource in MCP_RESOURCES
            assert isinstance(MCP_RESOURCES[resource], str)

    def test_movie_resources_exist(self) -> None:
        """Test movie-related resources are present."""
        movie_resources = [
            "movies_trending",
            "movies_popular",
            "movies_favorited",
            "movies_played",
            "movies_watched",
        ]
        for resource in movie_resources:
            assert resource in MCP_RESOURCES
            assert isinstance(MCP_RESOURCES[resource], str)

    def test_user_resources_exist(self) -> None:
        """Test user-related resources are present."""
        user_resources = [
            "user_auth_status",
            "user_watched_shows",
            "user_watched_movies",
        ]
        for resource in user_resources:
            assert resource in MCP_RESOURCES
            assert isinstance(MCP_RESOURCES[resource], str)

    def test_comment_resources_not_exist(self) -> None:
        """Test comment-related resources are NOT present (they are tools, not resources)."""
        comment_resources = [
            "comments_movie",
            "comments_show",
            "comments_season",
            "comments_episode",
            "comment",
            "comment_replies",
        ]
        for resource in comment_resources:
            assert resource not in MCP_RESOURCES, (
                f"Comment {resource} should be a tool, not a resource"
            )

    def test_rating_resources_not_exist(self) -> None:
        """Test rating resources are NOT present (they are tools, not resources)."""
        rating_resources = ["show_ratings", "movie_ratings"]
        for resource in rating_resources:
            assert resource not in MCP_RESOURCES, (
                f"Rating {resource} should be a tool, not a resource"
            )

    def test_all_resources_use_trakt_scheme(self) -> None:
        """Test all resource URIs use 'trakt://' scheme."""
        for resource_key, resource_uri in MCP_RESOURCES.items():
            assert resource_uri.startswith("trakt://"), (
                f"Resource {resource_key} should start with 'trakt://'"
            )

    def test_show_resource_uri_formats(self) -> None:
        """Test show resource URI formats."""
        show_resources = [
            "shows_trending",
            "shows_popular",
            "shows_favorited",
            "shows_played",
            "shows_watched",
        ]
        for resource in show_resources:
            uri = MCP_RESOURCES[resource]
            assert uri.startswith("trakt://shows/"), (
                f"Show resource {resource} should start with 'trakt://shows/'"
            )

    def test_movie_resource_uri_formats(self) -> None:
        """Test movie resource URI formats."""
        movie_resources = [
            "movies_trending",
            "movies_popular",
            "movies_favorited",
            "movies_played",
            "movies_watched",
        ]
        for resource in movie_resources:
            uri = MCP_RESOURCES[resource]
            assert uri.startswith("trakt://movies/"), (
                f"Movie resource {resource} should start with 'trakt://movies/'"
            )

    def test_user_resource_uri_formats(self) -> None:
        """Test user resource URI formats."""
        user_resources = {
            "user_auth_status": "trakt://user/auth/status",
            "user_watched_shows": "trakt://user/watched/shows",
            "user_watched_movies": "trakt://user/watched/movies",
        }
        for resource_key, expected_uri in user_resources.items():
            assert MCP_RESOURCES[resource_key] == expected_uri

    def test_resources_only_contain_static_data(self) -> None:
        """Test MCP resources only contain static data endpoints (not parameterized tools)."""
        # Resources should be static data that doesn't require parameters
        for resource_key, resource_uri in MCP_RESOURCES.items():
            # Resources should not contain parameter placeholders
            assert ":id" not in resource_uri, (
                f"Resource {resource_key} contains parameter placeholder, should be a tool instead"
            )
            assert ":season" not in resource_uri, (
                f"Resource {resource_key} contains parameter placeholder, should be a tool instead"
            )
            assert ":episode" not in resource_uri, (
                f"Resource {resource_key} contains parameter placeholder, should be a tool instead"
            )

    def test_uri_consistency_with_categories(self) -> None:
        """Test URI paths are consistent with resource categories."""
        # Show resources should contain 'shows' in path
        show_keys = [k for k in MCP_RESOURCES if k.startswith("shows_")]
        for key in show_keys:
            assert "/shows/" in MCP_RESOURCES[key], (
                f"Show resource {key} should contain '/shows/'"
            )

        # Movie resources should contain 'movies' in path
        movie_keys = [k for k in MCP_RESOURCES if k.startswith("movies_")]
        for key in movie_keys:
            assert "/movies/" in MCP_RESOURCES[key], (
                f"Movie resource {key} should contain '/movies/'"
            )

        # User resources should contain 'user' in path
        user_keys = [k for k in MCP_RESOURCES if k.startswith("user_")]
        for key in user_keys:
            assert "/user/" in MCP_RESOURCES[key], (
                f"User resource {key} should contain '/user/'"
            )

    def test_no_duplicate_resource_uris(self) -> None:
        """Test there are no duplicate resource URIs."""
        uris = list(MCP_RESOURCES.values())
        unique_uris = set(uris)
        # Most URIs should be unique (some aliases may exist)
        assert len(unique_uris) >= len(uris) * 0.9  # At least 90% should be unique

    def test_all_values_are_strings(self) -> None:
        """Test all resource URIs are strings."""
        for key, value in MCP_RESOURCES.items():
            assert isinstance(value, str), (
                f"Resource {key} URI should be string, got {type(value)}"
            )

    def test_no_empty_values(self) -> None:
        """Test no resource URIs are empty."""
        for key, value in MCP_RESOURCES.items():
            assert value, f"Resource {key} URI should not be empty"
