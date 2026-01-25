"""Tests for shows formatter module."""

from typing import TYPE_CHECKING, cast

from models.formatters.shows import ShowFormatters
from models.types.pagination import PaginatedResponse, PaginationMetadata

if TYPE_CHECKING:
    from models.types import ShowResponse, TrendingWrapper


class TestShowFormatters:
    """Test ShowFormatters class and methods."""

    def test_class_exists(self) -> None:
        """Test that ShowFormatters class exists."""
        assert ShowFormatters is not None

    def test_format_trending_shows_exists(self) -> None:
        """Test that format_trending_shows method exists."""
        assert hasattr(ShowFormatters, "format_trending_shows")
        assert callable(ShowFormatters.format_trending_shows)

    def test_format_trending_shows_with_empty_list(self) -> None:
        """Test formatting empty shows list."""
        result = ShowFormatters.format_trending_shows([])
        assert isinstance(result, str)

    def test_format_trending_shows_with_data(self) -> None:
        """Test formatting shows with sample data."""
        sample_shows: list[TrendingWrapper] = [
            {
                "watchers": 100,
                "show": {
                    "title": "Test Show 1",
                    "year": 2023,
                    "ids": {"trakt": 1, "slug": "test-show-1"},
                },
            },
            {
                "watchers": 200,
                "show": {
                    "title": "Test Show 2",
                    "year": 2024,
                    "ids": {"trakt": 2, "slug": "test-show-2"},
                },
            },
        ]
        result = ShowFormatters.format_trending_shows(sample_shows)
        assert isinstance(result, str)
        assert "Test Show 1" in result
        assert "Test Show 2" in result

    def test_has_additional_formatter_methods(self) -> None:
        """Test that additional formatter methods exist."""
        # Check for other common show formatting methods
        expected_methods = [
            "format_trending_shows",
            "format_popular_shows",
            "format_favorited_shows",
            "format_played_shows",
            "format_watched_shows",
            "format_show_summary",
            "format_show_extended",
        ]

        for method_name in expected_methods:
            if hasattr(ShowFormatters, method_name):
                assert callable(getattr(ShowFormatters, method_name))

    def test_all_methods_are_static(self) -> None:
        """Test that all public methods are static methods."""
        for attr_name in dir(ShowFormatters):
            if not attr_name.startswith("_") and callable(
                getattr(ShowFormatters, attr_name)
            ):
                attr = ShowFormatters.__dict__.get(attr_name)
                if attr is not None:
                    assert isinstance(attr, staticmethod), (
                        f"Method {attr_name} should be static"
                    )

    def test_format_show_summary(self) -> None:
        """Test format_show_summary with basic show data."""
        show_data = cast(
            "ShowResponse",
            {
                "title": "Breaking Bad",
                "year": 2008,
                "ids": {"trakt": 54321},
            },
        )
        result = ShowFormatters.format_show_summary(show_data)
        assert isinstance(result, str)
        assert "## Breaking Bad (2008)" in result
        assert "Trakt ID: 54321" in result

    def test_format_show_summary_with_missing_data(self) -> None:
        """Test format_show_summary with missing fields."""
        show_data = cast("ShowResponse", {"title": "Test Show"})
        result = ShowFormatters.format_show_summary(show_data)
        assert isinstance(result, str)
        assert "Test Show" in result

    def test_format_show_summary_empty_data(self) -> None:
        """Test format_show_summary with empty data."""
        result = ShowFormatters.format_show_summary(cast("ShowResponse", {}))
        assert isinstance(result, str)
        assert "No show data available." in result

    def test_format_show_extended(self) -> None:
        """Test format_show_extended with comprehensive show data."""
        show_data = cast(
            "ShowResponse",
            {
                "title": "Game of Thrones",
                "year": 2011,
                "ids": {"trakt": 1},
                "tagline": "Winter Is Coming",
                "overview": "An epic fantasy drama series.",
                "first_aired": "2011-04-18T01:00:00.000Z",
                "airs": {
                    "day": "Sunday",
                    "time": "21:00",
                    "timezone": "America/New_York",
                },
                "runtime": 60,
                "certification": "TV-MA",
                "network": "HBO",
                "country": "us",
                "status": "returning_series",
                "rating": 9.0,
                "votes": 111,
                "comment_count": 92,
                "languages": ["en"],
                "genres": ["drama", "fantasy"],
                "aired_episodes": 50,
                "homepage": "http://www.hbo.com/game-of-thrones/",
            },
        )
        result = ShowFormatters.format_show_extended(show_data)
        assert isinstance(result, str)
        assert "## Game of Thrones (2011) - Returning Series" in result
        assert "*Winter Is Coming*" in result
        assert "An epic fantasy drama series." in result
        assert "- Status: returning series" in result
        assert "- Runtime: 60 minutes" in result
        assert "- Certification: TV-MA" in result
        assert "- Network: HBO" in result
        assert "- Air Time: Sundays at 21:00 (America/New_York)" in result
        assert "- Aired Episodes: 50" in result
        assert "- Country: US" in result
        assert "- Genres: drama, fantasy" in result
        assert "- Languages: en" in result
        assert "- Homepage: http://www.hbo.com/game-of-thrones/" in result
        assert "- Rating: 9.0/10 (111 votes)" in result
        assert "- Comments: 92" in result
        assert "Trakt ID: 1" in result

    def test_format_show_extended_with_partial_data(self) -> None:
        """Test format_show_extended with partial data."""
        show_data = cast(
            "ShowResponse",
            {
                "title": "Test Show",
                "year": 2023,
                "status": "pilot",
                "rating": 7.5,
                "votes": 50,
                "airs": {"day": "Monday"},
            },
        )
        result = ShowFormatters.format_show_extended(show_data)
        assert isinstance(result, str)
        assert "## Test Show (2023) - Pilot" in result
        assert "- Status: pilot" in result
        assert "- Air Time: Mondays" in result
        assert "- Rating: 7.5/10 (50 votes)" in result
        # Ensure optional fields don't appear
        assert "- Runtime:" not in result
        assert "- Certification:" not in result
        assert "- Network:" not in result
        assert "- Aired Episodes:" not in result
        assert "- Genres:" not in result
        assert "- Languages:" not in result
        assert "- Homepage:" not in result
        assert "- Comments:" not in result

    def test_format_show_extended_with_partial_airs(self) -> None:
        """Test format_show_extended with partial airs data."""
        show_data = cast(
            "ShowResponse",
            {
                "title": "Test Show",
                "year": 2023,
                "airs": {"time": "20:00", "timezone": "UTC"},
            },
        )
        result = ShowFormatters.format_show_extended(show_data)
        assert isinstance(result, str)
        assert "- Air Time: at 20:00 (UTC)" in result

    def test_format_related_shows_exists(self) -> None:
        """Test that format_related_shows method exists."""
        assert hasattr(ShowFormatters, "format_related_shows")
        assert callable(ShowFormatters.format_related_shows)

    def test_format_related_shows_with_data(self) -> None:
        """Test formatting related shows with sample data."""
        sample_shows: list["ShowResponse"] = [
            cast(
                "ShowResponse",
                {
                    "title": "Better Call Saul",
                    "year": 2015,
                    "overview": "A prequel to the award-winning series Breaking Bad.",
                    "ids": {"trakt": 59660, "slug": "better-call-saul"},
                },
            ),
            cast(
                "ShowResponse",
                {
                    "title": "The Wire",
                    "year": 2002,
                    "overview": "A crime drama set in Baltimore.",
                    "ids": {"trakt": 1234, "slug": "the-wire"},
                },
            ),
        ]
        result = ShowFormatters.format_related_shows(sample_shows)
        assert isinstance(result, str)
        assert "# Related Shows" in result
        assert "Better Call Saul (2015)" in result
        assert "The Wire (2002)" in result
        assert "A prequel to the award-winning series Breaking Bad." in result

    def test_format_related_shows_empty(self) -> None:
        """Test formatting empty related shows list."""
        result = ShowFormatters.format_related_shows([])
        assert isinstance(result, str)
        assert "# Related Shows" in result
        assert "No related shows found." in result

    def test_format_related_shows_with_pagination(self) -> None:
        """Test formatting related shows with pagination metadata."""
        sample_shows: list["ShowResponse"] = [
            cast(
                "ShowResponse",
                {
                    "title": "Better Call Saul",
                    "year": 2015,
                    "ids": {"trakt": 59660, "slug": "better-call-saul"},
                },
            )
        ]
        paginated_response: PaginatedResponse["ShowResponse"] = PaginatedResponse(
            data=sample_shows,
            pagination=PaginationMetadata(
                current_page=2,
                items_per_page=10,
                total_pages=3,
                total_items=25,
            ),
        )
        result = ShowFormatters.format_related_shows(paginated_response)
        assert isinstance(result, str)
        assert "# Related Shows" in result
        assert "Better Call Saul (2015)" in result
        # Assert specific pagination output from format_pagination_header
        assert "Page 2 of 3" in result
        assert "of 25" in result  # Total items shown as "items X-Y of 25"
        # Navigation hints should appear since page 2 has both previous and next
        assert "Previous: page 1" in result
        assert "Next: page 3" in result

    def test_format_related_shows_truncates_overview(self) -> None:
        """Test that long overviews are truncated to 200 characters."""
        long_overview = "A" * 300  # 300 character overview
        sample_shows: list["ShowResponse"] = [
            cast(
                "ShowResponse",
                {
                    "title": "Test Show",
                    "year": 2023,
                    "overview": long_overview,
                    "ids": {"trakt": 1, "slug": "test-show"},
                },
            )
        ]
        result = ShowFormatters.format_related_shows(sample_shows)
        assert isinstance(result, str)
        # Should be truncated with ellipsis
        assert "..." in result
        # Should not contain the full 300 character string
        assert long_overview not in result
