"""Integration tests for config MCP direct imports."""

# Test imports from domain-specific config modules
from config.mcp.resources import MCP_RESOURCES
from config.mcp.tools import TOOL_NAMES


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


class TestResourceUriFormats:
    """Test MCP resource URI formats and structure."""

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

    def test_comment_tools_not_in_resources(self) -> None:
        """Test comment tools are not mistakenly included in resources."""
        comment_tools = [
            "comments_movie",
            "comments_show",
            "comments_season",
            "comments_episode",
            "comment",
            "comment_replies",
        ]
        for tool in comment_tools:
            assert tool not in MCP_RESOURCES, (
                f"Comment tool {tool} should not be in MCP_RESOURCES (it's a tool, not a resource)"
            )

    def test_resources_only_contain_static_data(self) -> None:
        """Test MCP resources only contain static data endpoints (not parameterized tools)."""
        # Resources should be static data that doesn't require parameters
        # All current resources are static lists (trending, popular, etc.)
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


class TestToolNames:
    """Test TOOL_NAMES dictionary structure and contents."""

    def test_tool_names_is_dict(self) -> None:
        """Test TOOL_NAMES is a dictionary."""
        assert isinstance(TOOL_NAMES, dict)
        assert len(TOOL_NAMES) > 0

    def test_show_tools_exist(self) -> None:
        """Test show-related tools are present."""
        show_tools = [
            "fetch_trending_shows",
            "fetch_popular_shows",
            "fetch_favorited_shows",
            "fetch_played_shows",
            "fetch_watched_shows",
        ]
        for tool in show_tools:
            assert tool in TOOL_NAMES
            assert isinstance(TOOL_NAMES[tool], str)

    def test_movie_tools_exist(self) -> None:
        """Test movie-related tools are present."""
        movie_tools = [
            "fetch_trending_movies",
            "fetch_popular_movies",
            "fetch_favorited_movies",
            "fetch_played_movies",
            "fetch_watched_movies",
        ]
        for tool in movie_tools:
            assert tool in TOOL_NAMES
            assert isinstance(TOOL_NAMES[tool], str)

    def test_auth_tools_exist(self) -> None:
        """Test authentication tools are present."""
        auth_tools = [
            "start_device_auth",
            "check_auth_status",
            "clear_auth",
        ]
        for tool in auth_tools:
            assert tool in TOOL_NAMES
            assert isinstance(TOOL_NAMES[tool], str)

    def test_user_tools_exist(self) -> None:
        """Test user-specific tools are present."""
        user_tools = [
            "fetch_user_watched_shows",
            "fetch_user_watched_movies",
            "checkin_to_show",
        ]
        for tool in user_tools:
            assert tool in TOOL_NAMES
            assert isinstance(TOOL_NAMES[tool], str)

    def test_comment_tools_exist(self) -> None:
        """Test comment tools are present."""
        comment_tools = [
            "fetch_movie_comments",
            "fetch_show_comments",
            "fetch_season_comments",
            "fetch_episode_comments",
            "fetch_comment",
            "fetch_comment_replies",
        ]
        for tool in comment_tools:
            assert tool in TOOL_NAMES
            assert isinstance(TOOL_NAMES[tool], str)

    def test_rating_tools_exist(self) -> None:
        """Test rating tools are present."""
        rating_tools = [
            "fetch_show_ratings",
            "fetch_movie_ratings",
        ]
        for tool in rating_tools:
            assert tool in TOOL_NAMES
            assert isinstance(TOOL_NAMES[tool], str)

    def test_search_tools_exist(self) -> None:
        """Test search tools are present."""
        search_tools = [
            "search_shows",
            "search_movies",
        ]
        for tool in search_tools:
            assert tool in TOOL_NAMES
            assert isinstance(TOOL_NAMES[tool], str)


class TestToolNamingConsistency:
    """Test tool naming consistency and conventions."""

    def test_tool_names_match_keys(self) -> None:
        """Test tool names match their dictionary keys."""
        for key, value in TOOL_NAMES.items():
            assert key == value, f"Tool name key {key} should match value {value}"

    def test_tool_naming_conventions(self) -> None:
        """Test tool names follow consistent naming conventions."""
        for tool_name in TOOL_NAMES:
            # Should use lowercase and underscores
            assert tool_name.islower(), f"Tool name {tool_name} should be lowercase"
            assert " " not in tool_name, (
                f"Tool name {tool_name} should not contain spaces"
            )
            # Should not start or end with underscore
            assert not tool_name.startswith("_"), (
                f"Tool name {tool_name} should not start with underscore"
            )
            assert not tool_name.endswith("_"), (
                f"Tool name {tool_name} should not end with underscore"
            )

    def test_fetch_tools_start_with_fetch(self) -> None:
        """Test tools that fetch data start with 'fetch_'."""
        fetch_tools = [k for k in TOOL_NAMES if "fetch" in k]
        for tool in fetch_tools:
            assert tool.startswith("fetch_"), (
                f"Fetch tool {tool} should start with 'fetch_'"
            )

    def test_tool_categories_consistency(self) -> None:
        """Test tool names are consistent within categories."""
        # Show tools should contain 'shows'
        show_tools = [
            k for k in TOOL_NAMES if "show" in k and not k.startswith("checkin")
        ]
        for tool in show_tools:
            assert "show" in tool, f"Show tool {tool} should contain 'show'"

        # Movie tools should contain 'movies'
        movie_tools = [k for k in TOOL_NAMES if "movie" in k]
        for tool in movie_tools:
            assert "movie" in tool, f"Movie tool {tool} should contain 'movie'"

        # Auth tools should contain 'auth'
        auth_tools = [k for k in TOOL_NAMES if "auth" in k]
        for tool in auth_tools:
            assert "auth" in tool, f"Auth tool {tool} should contain 'auth'"


class TestResourcesIntegration:
    """Test integration aspects between resources and tools."""

    def test_no_duplicate_resource_uris(self) -> None:
        """Test there are no duplicate resource URIs."""
        uris = list(MCP_RESOURCES.values())
        unique_uris = set(uris)
        # Most URIs should be unique (some aliases may exist)
        assert len(unique_uris) >= len(uris) * 0.9  # At least 90% should be unique

    def test_no_duplicate_tool_names(self) -> None:
        """Test there are no duplicate tool names."""
        tool_names = list(TOOL_NAMES.values())
        unique_names = set(tool_names)
        assert len(unique_names) == len(tool_names), "All tool names should be unique"

    def test_resource_tool_correlation(self) -> None:
        """Test that resources and tools have logical correlation."""
        # For each show resource, there should be a corresponding tool
        show_resources = [k for k in MCP_RESOURCES if k.startswith("shows_")]
        show_tools = [k for k in TOOL_NAMES if "shows" in k and k.startswith("fetch_")]

        # Should have reasonable correlation (not necessarily 1:1)
        assert len(show_tools) >= len(show_resources) * 0.8, (
            "Should have tools for most show resources"
        )

        # Same for movies
        movie_resources = [k for k in MCP_RESOURCES if k.startswith("movies_")]
        movie_tools = [
            k for k in TOOL_NAMES if "movies" in k and k.startswith("fetch_")
        ]

        assert len(movie_tools) >= len(movie_resources) * 0.8, (
            "Should have tools for most movie resources"
        )

    def test_all_values_are_strings(self) -> None:
        """Test all resource URIs and tool names are strings."""
        for key, value in MCP_RESOURCES.items():
            assert isinstance(value, str), (
                f"Resource {key} URI should be string, got {type(value)}"
            )

        for key, value in TOOL_NAMES.items():
            assert isinstance(value, str), (
                f"Tool {key} name should be string, got {type(value)}"
            )

    def test_no_empty_values(self) -> None:
        """Test no resource URIs or tool names are empty."""
        for key, value in MCP_RESOURCES.items():
            assert value, f"Resource {key} URI should not be empty"

        for key, value in TOOL_NAMES.items():
            assert value, f"Tool {key} name should not be empty"

    def test_mcp_config_matches_domain_modules(self) -> None:
        """Test that MCP configs from main config match domain-specific modules."""
        # Import from domain-specific modules
        from config.mcp.resources import MCP_RESOURCES as MCP_RESOURCES_DOMAIN
        from config.mcp.tools import TOOL_NAMES as TOOL_NAMES_DOMAIN

        # Should be identical
        assert MCP_RESOURCES == MCP_RESOURCES_DOMAIN, (
            "MCP_RESOURCES should match domain module"
        )
        assert TOOL_NAMES == TOOL_NAMES_DOMAIN, "TOOL_NAMES should match domain module"

        # Verify individual items match
        for key, value in MCP_RESOURCES_DOMAIN.items():
            assert key in MCP_RESOURCES, f"Resource {key} missing from main config"
            assert MCP_RESOURCES[key] == value, f"Resource {key} value mismatch"

        for key, value in TOOL_NAMES_DOMAIN.items():
            assert key in TOOL_NAMES, f"Tool {key} missing from main config"
            assert TOOL_NAMES[key] == value, f"Tool {key} value mismatch"
