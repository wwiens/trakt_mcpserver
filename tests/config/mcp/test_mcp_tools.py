"""Tests for MCP tools module."""

from config.mcp.tools import TOOL_NAMES


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

    def test_no_duplicate_tool_names(self) -> None:
        """Test there are no duplicate tool names."""
        tool_names = list(TOOL_NAMES.values())
        unique_names = set(tool_names)
        assert len(unique_names) == len(tool_names), "All tool names should be unique"

    def test_all_values_are_strings(self) -> None:
        """Test all tool names are strings."""
        for key, value in TOOL_NAMES.items():
            assert isinstance(value, str), (
                f"Tool {key} name should be string, got {type(value)}"
            )

    def test_no_empty_values(self) -> None:
        """Test no tool names are empty."""
        for key, value in TOOL_NAMES.items():
            assert value, f"Tool {key} name should not be empty"
