"""Tests for MCP tools module."""

from config.mcp.tools import (
    AUTH_TOOLS,
    CHECKIN_TOOLS,
    COMMENT_TOOLS,
    EPISODE_TOOLS,
    MOVIE_TOOLS,
    PEOPLE_TOOLS,
    PROGRESS_TOOLS,
    RECOMMENDATIONS_TOOLS,
    SEARCH_TOOLS,
    SEASON_TOOLS,
    SHOW_TOOLS,
    SYNC_TOOLS,
    TOOL_NAMES,
    USER_TOOLS,
)


class TestToolNames:
    """Test TOOL_NAMES frozenset structure and contents."""

    def test_tool_names_is_frozenset(self) -> None:
        """Test TOOL_NAMES is a non-empty frozenset."""
        assert isinstance(TOOL_NAMES, frozenset)
        assert len(TOOL_NAMES) > 0

    def test_show_tools_exist(self) -> None:
        """Test show-related tools are present."""
        show_tools = [
            "fetch_trending_shows",
            "fetch_popular_shows",
            "fetch_favorited_shows",
            "fetch_played_shows",
            "fetch_watched_shows",
            "fetch_anticipated_shows",
        ]
        for tool in show_tools:
            assert tool in TOOL_NAMES

    def test_movie_tools_exist(self) -> None:
        """Test movie-related tools are present."""
        movie_tools = [
            "fetch_trending_movies",
            "fetch_popular_movies",
            "fetch_favorited_movies",
            "fetch_played_movies",
            "fetch_watched_movies",
            "fetch_anticipated_movies",
        ]
        for tool in movie_tools:
            assert tool in TOOL_NAMES

    def test_auth_tools_exist(self) -> None:
        """Test authentication tools are present."""
        auth_tools = [
            "start_device_auth",
            "check_auth_status",
            "clear_auth",
        ]
        for tool in auth_tools:
            assert tool in TOOL_NAMES

    def test_user_tools_exist(self) -> None:
        """Test user-specific tools are present."""
        user_tools = [
            "fetch_user_watched_shows",
            "fetch_user_watched_movies",
            "checkin_to_show",
        ]
        for tool in user_tools:
            assert tool in TOOL_NAMES

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

    def test_rating_tools_exist(self) -> None:
        """Test rating tools are present."""
        rating_tools = [
            "fetch_show_ratings",
            "fetch_movie_ratings",
        ]
        for tool in rating_tools:
            assert tool in TOOL_NAMES

    def test_search_tools_exist(self) -> None:
        """Test search tools are present."""
        search_tools = [
            "search_shows",
            "search_movies",
        ]
        for tool in search_tools:
            assert tool in TOOL_NAMES

    def test_tool_naming_conventions(self) -> None:
        """Test tool names follow consistent naming conventions."""
        for tool_name in TOOL_NAMES:
            assert tool_name.islower(), f"Tool name {tool_name} should be lowercase"
            assert " " not in tool_name, (
                f"Tool name {tool_name} should not contain spaces"
            )
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
        show_tools = [
            k for k in TOOL_NAMES if "show" in k and not k.startswith("checkin")
        ]
        for tool in show_tools:
            assert "show" in tool, f"Show tool {tool} should contain 'show'"

        movie_tools = [k for k in TOOL_NAMES if "movie" in k]
        for tool in movie_tools:
            assert "movie" in tool, f"Movie tool {tool} should contain 'movie'"

        auth_tools = [k for k in TOOL_NAMES if "auth" in k]
        for tool in auth_tools:
            assert "auth" in tool, f"Auth tool {tool} should contain 'auth'"

    def test_domain_sets_are_disjoint(self) -> None:
        """Each tool should belong to exactly one domain set."""
        domain_sets = {
            "SHOW_TOOLS": SHOW_TOOLS,
            "MOVIE_TOOLS": MOVIE_TOOLS,
            "PEOPLE_TOOLS": PEOPLE_TOOLS,
            "AUTH_TOOLS": AUTH_TOOLS,
            "USER_TOOLS": USER_TOOLS,
            "CHECKIN_TOOLS": CHECKIN_TOOLS,
            "COMMENT_TOOLS": COMMENT_TOOLS,
            "EPISODE_TOOLS": EPISODE_TOOLS,
            "PROGRESS_TOOLS": PROGRESS_TOOLS,
            "RECOMMENDATIONS_TOOLS": RECOMMENDATIONS_TOOLS,
            "SEARCH_TOOLS": SEARCH_TOOLS,
            "SEASON_TOOLS": SEASON_TOOLS,
            "SYNC_TOOLS": SYNC_TOOLS,
        }
        names = list(domain_sets)
        for i, a_name in enumerate(names):
            for b_name in names[i + 1 :]:
                overlap = domain_sets[a_name] & domain_sets[b_name]
                assert not overlap, f"{a_name} and {b_name} share tool names: {overlap}"

    def test_tool_names_equals_union_of_domain_sets(self) -> None:
        """TOOL_NAMES should be the exact union of every domain frozenset."""
        union = (
            SHOW_TOOLS
            | MOVIE_TOOLS
            | PEOPLE_TOOLS
            | AUTH_TOOLS
            | USER_TOOLS
            | CHECKIN_TOOLS
            | COMMENT_TOOLS
            | EPISODE_TOOLS
            | PROGRESS_TOOLS
            | RECOMMENDATIONS_TOOLS
            | SEARCH_TOOLS
            | SEASON_TOOLS
            | SYNC_TOOLS
        )
        assert union == TOOL_NAMES
