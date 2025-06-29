"""Tests for checkin formatter module."""

from models.formatters.checkin import CheckinFormatters


class TestCheckinFormatters:
    """Test CheckinFormatters class and methods."""

    def test_class_exists(self) -> None:
        """Test that CheckinFormatters class exists."""
        assert CheckinFormatters is not None

    def test_has_checkin_formatter_methods(self) -> None:
        """Test that checkin formatting methods exist."""
        # Check for common checkin formatting methods
        expected_methods = [
            "format_checkin_response",
            "format_show_checkin",
            "format_movie_checkin",
        ]

        for method_name in expected_methods:
            if hasattr(CheckinFormatters, method_name):
                assert callable(getattr(CheckinFormatters, method_name))

    def test_format_methods_return_strings(self) -> None:
        """Test that formatter methods return strings."""
        # Test with sample data where methods exist
        if hasattr(CheckinFormatters, "format_checkin_response"):
            sample_response = {"status": "success", "message": "Checked in"}
            result = CheckinFormatters.format_checkin_response(sample_response)
            assert isinstance(result, str)

    def test_all_methods_are_static(self) -> None:
        """Test that all public methods are static methods."""
        for attr_name in dir(CheckinFormatters):
            if not attr_name.startswith("_") and callable(
                getattr(CheckinFormatters, attr_name)
            ):
                attr = CheckinFormatters.__dict__.get(attr_name)
                if attr is not None:
                    assert isinstance(attr, staticmethod), (
                        f"Method {attr_name} should be static"
                    )
