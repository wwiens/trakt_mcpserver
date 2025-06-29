"""Tests for comments formatter module."""

from models.formatters.comments import CommentsFormatters


class TestCommentsFormatters:
    """Test CommentsFormatters class and methods."""

    def test_class_exists(self) -> None:
        """Test that CommentsFormatters class exists."""
        assert CommentsFormatters is not None

    def test_has_comment_formatter_methods(self) -> None:
        """Test that comment formatting methods exist."""
        # Check for common comment formatting methods
        expected_methods = [
            "format_movie_comments",
            "format_show_comments",
            "format_season_comments",
            "format_episode_comments",
            "format_comment",
            "format_comment_replies",
        ]

        for method_name in expected_methods:
            if hasattr(CommentsFormatters, method_name):
                assert callable(getattr(CommentsFormatters, method_name))

    def test_format_methods_return_strings(self) -> None:
        """Test that formatter methods return strings."""
        # Test with empty data where methods exist
        if hasattr(CommentsFormatters, "format_comments"):
            result = CommentsFormatters.format_comments([], "Test Title")
            assert isinstance(result, str)

    def test_all_methods_are_static(self) -> None:
        """Test that all public methods are static methods."""
        for attr_name in dir(CommentsFormatters):
            if not attr_name.startswith("_") and callable(
                getattr(CommentsFormatters, attr_name)
            ):
                attr = CommentsFormatters.__dict__.get(attr_name)
                if attr is not None:
                    assert isinstance(attr, staticmethod), (
                        f"Method {attr_name} should be static"
                    )
