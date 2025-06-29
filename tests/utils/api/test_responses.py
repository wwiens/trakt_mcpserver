"""Tests for utils.api.responses module."""

from typing import Any

import pytest

from utils.api.responses import format_error_response


class TestFormatErrorResponse:
    """Test format_error_response helper function."""

    def test_format_error_response_basic(self) -> None:
        """Test basic error response formatting."""
        message = "Test error message"
        result = format_error_response(message)

        expected = {
            "error": True,
            "message": message,
        }

        assert result == expected
        assert isinstance(result, dict)

    def test_format_error_response_empty_message(self) -> None:
        """Test error response formatting with empty message."""
        message = ""
        result = format_error_response(message)

        expected = {
            "error": True,
            "message": "",
        }

        assert result == expected

    def test_format_error_response_long_message(self) -> None:
        """Test error response formatting with long message."""
        message = (
            "This is a very long error message that contains multiple sentences. "
            "It should be handled properly by the format_error_response function. "
            "The function should preserve the entire message without truncation."
        )

        result = format_error_response(message)

        expected = {
            "error": True,
            "message": message,
        }

        assert result == expected
        assert result["message"] == message

    def test_format_error_response_special_characters(self) -> None:
        """Test error response formatting with special characters."""
        message = "Error: Connection failed! @#$%^&*()[]{}|\\:;\"'<>?,./"
        result = format_error_response(message)

        expected = {
            "error": True,
            "message": message,
        }

        assert result == expected

    def test_format_error_response_unicode_characters(self) -> None:
        """Test error response formatting with unicode characters."""
        message = "Error: 连接失败 🚫 Échec de connexion ñoña"
        result = format_error_response(message)

        expected = {
            "error": True,
            "message": message,
        }

        assert result == expected

    def test_format_error_response_multiline_message(self) -> None:
        """Test error response formatting with multiline message."""
        message = "Line 1 of error\nLine 2 of error\nLine 3 of error"
        result = format_error_response(message)

        expected = {
            "error": True,
            "message": message,
        }

        assert result == expected

    def test_format_error_response_return_type(self) -> None:
        """Test that format_error_response returns correct type."""
        message = "Test message"
        result = format_error_response(message)

        assert isinstance(result, dict)
        assert isinstance(result["error"], bool)
        assert isinstance(result["message"], str)

    def test_format_error_response_error_flag_always_true(self) -> None:
        """Test that error flag is always True regardless of message."""
        test_messages = [
            "Normal error",
            "",
            "Success message",  # Even if message says success, error flag should be True
            "Error: False",  # Even if message contains "False", error flag should be True
        ]

        for message in test_messages:
            result = format_error_response(message)
            assert result["error"] is True, (
                f"Error flag should be True for message: {message}"
            )

    def test_format_error_response_preserves_message_exactly(self) -> None:
        """Test that the message is preserved exactly as passed."""
        test_messages = [
            "Test",
            " Leading and trailing spaces ",
            "\tTabs and newlines\n",
            "UPPERCASE and lowercase",
            "123456789",
            "Mixed: text, numbers 123, symbols @#$%",
        ]

        for message in test_messages:
            result = format_error_response(message)
            assert result["message"] == message, (
                f"Message should be preserved exactly: {message}"
            )

    def test_format_error_response_structure(self) -> None:
        """Test that the response has the correct structure."""
        message = "Test error"
        result = format_error_response(message)

        # Should have exactly 2 keys
        assert len(result) == 2
        assert "error" in result
        assert "message" in result

        # Should not have any other keys
        expected_keys = {"error", "message"}
        assert set(result.keys()) == expected_keys

    def test_format_error_response_immutability(self) -> None:
        """Test that the function doesn't modify the input message."""
        original_message = "Original error message"
        message_copy = original_message  # String is immutable, but good to test

        result = format_error_response(message_copy)

        # Original message should be unchanged
        assert message_copy == original_message
        assert result["message"] == original_message

    def test_format_error_response_with_none_like_strings(self) -> None:
        """Test error response formatting with None-like string values."""
        test_messages = [
            "None",
            "null",
            "undefined",
            "nil",
        ]

        for message in test_messages:
            result = format_error_response(message)
            expected = {
                "error": True,
                "message": message,
            }
            assert result == expected


class TestHelpersIntegration:
    """Test integration aspects of helpers module."""

    def test_format_error_response_matches_expected_api_format(self) -> None:
        """Test that error response format matches expected API response format."""
        message = "API request failed"
        result = format_error_response(message)

        # Should match the format expected by API consumers
        assert "error" in result
        assert "message" in result
        assert result["error"] is True
        assert isinstance(result["message"], str)

        # Should be JSON serializable
        import json

        try:
            json.dumps(result)
        except (TypeError, ValueError):
            pytest.fail("Error response should be JSON serializable")

    def test_format_error_response_consistent_with_error_handling(self) -> None:
        """Test that error response format is consistent with error handling patterns."""
        # This test ensures the helper integrates well with the decorator error handling
        common_error_messages = [
            "Error: Unauthorized. Please check your Trakt API credentials.",
            "Error: The requested resource was not found.",
            "Error: Rate limit exceeded. Please try again later.",
            "Error: Unable to connect to Trakt API. Please check your internet connection.",
            "Error: An unexpected error occurred: ValueError",
        ]

        for message in common_error_messages:
            result = format_error_response(message)

            # Should follow consistent format
            assert result["error"] is True
            assert result["message"] == message
            assert len(result) == 2

    def test_all_helper_functions_exist(self) -> None:
        """Test that all expected helper functions are available."""
        import utils.api.responses as helpers

        # Currently only format_error_response exists, but this test
        # can be extended as more helpers are added
        expected_functions = [
            "format_error_response",
        ]

        for func_name in expected_functions:
            assert hasattr(helpers, func_name), (
                f"Helper function {func_name} should exist"
            )
            assert callable(getattr(helpers, func_name)), (
                f"Helper {func_name} should be callable"
            )

    def test_helpers_module_structure(self) -> None:
        """Test the overall structure of the helpers module."""
        import utils.api.responses as helpers

        # Should have proper docstring
        assert helpers.__doc__ is not None
        assert "helper" in helpers.__doc__.lower()

        # Should export the expected functions
        public_functions = [name for name in dir(helpers) if not name.startswith("_")]
        assert "format_error_response" in public_functions

    def test_type_annotations_consistency(self) -> None:
        """Test that type annotations are consistent and correct."""
        import inspect

        from utils.api.responses import format_error_response

        sig = inspect.signature(format_error_response)

        # Should have proper parameter annotation
        message_param = sig.parameters["message"]
        assert message_param.annotation is str

        # Should have proper return annotation
        return_annotation = sig.return_annotation
        assert return_annotation == dict[str, Any]
