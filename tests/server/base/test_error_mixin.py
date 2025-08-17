"""Tests for the base error handling mixin."""

from typing import Any

import pytest

from server.base.error_mixin import (
    BaseToolErrorMixin,
    is_sensitive_key,
    sanitize_args,
    sanitize_kwargs,
    sanitize_value,
)
from utils.api.errors import InternalError


class TestSanitizationFunctions:
    """Test the parameter sanitization functions."""

    def test_is_sensitive_key(self) -> None:
        """Test detection of sensitive parameter names."""
        # Sensitive keys
        assert is_sensitive_key("access_token") is True
        assert is_sensitive_key("refresh_token") is True
        assert is_sensitive_key("client_secret") is True
        assert is_sensitive_key("api_key") is True
        assert is_sensitive_key("device_code") is True
        assert is_sensitive_key("authorization") is True
        assert is_sensitive_key("password") is True

        # Case insensitive
        assert is_sensitive_key("ACCESS_TOKEN") is True
        assert is_sensitive_key("Client_Secret") is True

        # Partial matches
        assert is_sensitive_key("user_access_token") is True
        assert is_sensitive_key("my_password_field") is True
        assert is_sensitive_key("auth_header") is True

        # Non-sensitive keys
        assert is_sensitive_key("username") is False
        assert is_sensitive_key("email") is False
        assert is_sensitive_key("user_id") is False
        assert is_sensitive_key("show_id") is False
        assert is_sensitive_key("client_id") is False  # client_id is public

    def testsanitize_value_with_sensitive_key(self) -> None:
        """Test value sanitization when key indicates sensitivity."""
        # Sensitive keys always redact values
        assert sanitize_value("my-secret-value", "access_token") == "[REDACTED]"
        assert sanitize_value("12345", "password") == "[REDACTED]"
        assert sanitize_value({"nested": "data"}, "api_key") == "[REDACTED]"

    def testsanitize_value_string_patterns(self) -> None:
        """Test sanitization of string values with sensitive patterns."""
        # Bearer tokens
        assert sanitize_value("Bearer abc123") == "[REDACTED]"
        assert sanitize_value("bearer xyz789") == "[REDACTED]"

        # Token patterns
        assert sanitize_value("token:abc123") == "[REDACTED]"
        assert sanitize_value("secret:mysecret") == "[REDACTED]"
        assert sanitize_value("password:12345") == "[REDACTED]"

        # Regular strings pass through
        assert sanitize_value("Hello world") == "Hello world"
        assert sanitize_value("user@example.com") == "user@example.com"

    def testsanitize_value_long_random_strings(self) -> None:
        """Test sanitization of long random strings that might be tokens."""
        # Long random string with token-like key
        long_token = "abcdef1234567890abcdef1234567890"
        assert sanitize_value(long_token, "auth_token") == "[REDACTED]"
        assert sanitize_value(long_token, "device_code") == "[REDACTED]"

        # Long random string without sensitive key context
        assert sanitize_value(long_token, "description") == long_token
        assert sanitize_value(long_token, None) == long_token

        # Short strings don't get redacted
        assert sanitize_value("abc123", "token") == "[REDACTED]"  # But key is sensitive
        assert sanitize_value("abc123", "name") == "abc123"

    def testsanitize_value_nested_structures(self) -> None:
        """Test sanitization of nested dictionaries and lists."""
        # Dictionary with sensitive keys
        data = {
            "username": "john",
            "access_token": "secret123",
            "profile": {"email": "john@example.com", "api_key": "key456"},
        }
        result = sanitize_value(data)
        assert result["username"] == "john"
        assert result["access_token"] == "[REDACTED]"
        assert result["profile"]["email"] == "john@example.com"
        assert result["profile"]["api_key"] == "[REDACTED]"

        # List with mixed values
        items = ["hello", "Bearer token123", {"password": "secret"}]
        result = sanitize_value(items)
        assert result[0] == "hello"
        assert result[1] == "[REDACTED]"
        assert result[2]["password"] == "[REDACTED]"

    def testsanitize_args(self) -> None:
        """Test sanitization of positional arguments."""
        # Empty args
        assert sanitize_args(()) == ""

        # Normal args
        args = ("user123", "show456", 42)
        assert "user123" in sanitize_args(args)
        assert "show456" in sanitize_args(args)
        assert "42" in sanitize_args(args)

        # Args with sensitive patterns
        args = ("Bearer token123", "normal_value", "secret:password")
        result = sanitize_args(args)
        assert "[REDACTED]" in result
        assert "normal_value" in result
        assert "secret:password" not in result

    def testsanitize_kwargs(self) -> None:
        """Test sanitization of keyword arguments."""
        # Empty kwargs
        assert sanitize_kwargs({}) == ""

        # Normal kwargs
        kwargs = {"user_id": "123", "show_id": "456", "limit": 10}
        result = sanitize_kwargs(kwargs)
        assert "123" in result
        assert "456" in result
        assert "10" in result

        # Kwargs with sensitive keys
        kwargs = {
            "user_id": "123",
            "access_token": "secret_token_value",
            "api_key": "my_api_key",
            "data": {"password": "secret123"},
        }
        result = sanitize_kwargs(kwargs)
        assert "'user_id': '123'" in result
        assert "'access_token': '[REDACTED]'" in result
        assert "'api_key': '[REDACTED]'" in result
        assert "'password': '[REDACTED]'" in result
        assert "secret_token_value" not in result
        assert "my_api_key" not in result
        assert "secret123" not in result


@pytest.mark.asyncio
class TestErrorHandlingDecorator:
    """Test the error handling decorator with sanitization."""

    async def test_with_error_handling_sanitizes_sensitive_args(self) -> None:
        """Test that sensitive args are sanitized in error data."""

        @BaseToolErrorMixin.with_error_handling("test_operation")
        async def failing_function(token: str, user_id: str) -> None:
            raise ValueError("Test error")

        with pytest.raises(InternalError) as exc_info:
            await failing_function("secret_token_123", "user456")

        error = exc_info.value
        error_data = error.data

        # Check that args were sanitized
        assert error_data is not None
        assert "args" in error_data
        assert "[REDACTED]" in error_data["args"]
        assert "secret_token_123" not in error_data["args"]
        assert "user456" in error_data["args"]  # Non-sensitive value preserved

    async def test_with_error_handling_sanitizes_sensitive_kwargs(self) -> None:
        """Test that sensitive kwargs are sanitized in error data."""

        @BaseToolErrorMixin.with_error_handling("test_operation")
        async def failing_function(**kwargs: Any) -> None:
            raise ValueError("Test error")

        with pytest.raises(InternalError) as exc_info:
            await failing_function(
                user_id="123",
                access_token="my_secret_token",
                client_secret="super_secret",
                show_id="456",
            )

        error = exc_info.value
        error_data = error.data

        # Check that kwargs were sanitized
        assert error_data is not None
        assert "kwargs" in error_data
        kwargs_str = error_data["kwargs"]
        assert "'access_token': '[REDACTED]'" in kwargs_str
        assert "'client_secret': '[REDACTED]'" in kwargs_str
        assert "'user_id': '123'" in kwargs_str
        assert "'show_id': '456'" in kwargs_str
        assert "my_secret_token" not in kwargs_str
        assert "super_secret" not in kwargs_str

    async def test_with_error_handling_preserves_non_sensitive_data(self) -> None:
        """Test that non-sensitive data is preserved in error data."""

        @BaseToolErrorMixin.with_error_handling("test_operation")
        async def failing_function(show_id: str, season: int, **kwargs: Any) -> None:
            raise ValueError("Test error")

        with pytest.raises(InternalError) as exc_info:
            await failing_function(
                "show123", 5, episode=10, include_metadata=True, user_name="john_doe"
            )

        error = exc_info.value
        error_data = error.data

        # Check that non-sensitive data is preserved
        assert error_data is not None
        assert "args" in error_data
        assert "show123" in error_data["args"]
        assert "5" in error_data["args"]

        assert "kwargs" in error_data
        kwargs_str = error_data["kwargs"]
        assert "'episode': 10" in kwargs_str
        assert "'include_metadata': True" in kwargs_str
        assert "'user_name': 'john_doe'" in kwargs_str
