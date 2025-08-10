"""Base error handling mixin for MCP tools."""

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from config.auth import AUTH_VERIFICATION_URL
from utils.api.error_types import AuthenticationRequiredError
from utils.api.errors import InternalError, InvalidParamsError, MCPError
from utils.api.request_context import add_context_to_error_data
from utils.api.structured_logging import get_structured_logger

logger = get_structured_logger("trakt_mcp.server.tools")

T = TypeVar("T")

# Sensitive parameter patterns that should be redacted in error logs
SENSITIVE_PARAM_PATTERNS = {
    "access_token",
    "refresh_token",
    "token",
    "password",
    "secret",
    "client_secret",
    "api_key",
    "device_code",
    "authorization",
    "auth",
    "credential",
    "key",
}


def is_sensitive_key(key: str) -> bool:
    """Check if a parameter name contains sensitive patterns.

    Args:
        key: The parameter name to check

    Returns:
        True if the key contains sensitive patterns
    """
    key_lower = key.lower()
    return any(pattern in key_lower for pattern in SENSITIVE_PARAM_PATTERNS)


def sanitize_value(value: Any, key: str | None = None) -> Any:
    """Sanitize a value, redacting if sensitive.

    Args:
        value: The value to sanitize
        key: Optional key name for context

    Returns:
        Sanitized value or "[REDACTED]" if sensitive
    """
    # Check if key indicates sensitive data
    if key and is_sensitive_key(key):
        return "[REDACTED]"

    # Check string values for sensitive patterns
    if isinstance(value, str):
        value_lower = value.lower()
        # Check if the string itself looks like a token/secret
        if any(
            pattern in value_lower
            for pattern in ["bearer ", "token:", "secret:", "password:"]
        ):
            return "[REDACTED]"
        # Check if string contains sensitive words
        if (
            any(
                word in value_lower
                for word in ["secret", "token", "password", "auth", "key"]
            )
            and len(value) > 10
            and (
                value.replace("-", "").replace("_", "").isalnum()
                or "_" in value
                or "-" in value
            )
        ):
            return "[REDACTED]"
        # Long random strings might be tokens
        if (
            len(value) > 20
            and value.replace("-", "").replace("_", "").isalnum()
            and key
            and any(word in key.lower() for word in ["token", "code", "auth", "key"])
        ):
            return "[REDACTED]"

    # Recursively sanitize dictionaries
    if isinstance(value, dict):
        result: dict[Any, Any] = {}
        for k, v in value.items():  # type: ignore[misc]
            result[k] = sanitize_value(v, str(k) if k else None)  # type: ignore[misc]
        return result

    # Recursively sanitize lists
    if isinstance(value, list | tuple):
        sanitized: list[Any] = [sanitize_value(item) for item in value]  # type: ignore[misc]
        if isinstance(value, tuple):
            return tuple(sanitized)
        return sanitized

    return value


def sanitize_args(args: tuple[Any, ...]) -> str:
    """Sanitize positional arguments for logging.

    Args:
        args: Tuple of positional arguments

    Returns:
        String representation with sensitive data redacted
    """
    if not args:
        return ""

    sanitized: list[Any] = []
    for arg in args:
        # For positional args, we don't have parameter names
        # so we need to be more careful
        sanitized_arg = sanitize_value(arg)
        sanitized.append(sanitized_arg)

    return str(tuple(sanitized))


def sanitize_kwargs(kwargs: dict[str, Any]) -> str:
    """Sanitize keyword arguments for logging.

    Args:
        kwargs: Dictionary of keyword arguments

    Returns:
        String representation with sensitive data redacted
    """
    if not kwargs:
        return ""

    sanitized: dict[str, Any] = {}
    for key, value in kwargs.items():
        if is_sensitive_key(key):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = sanitize_value(value, key)

    return str(sanitized)


class BaseToolErrorMixin:
    """Mixin providing standardized error handling for MCP tools.

    This mixin ensures all tools follow consistent error handling patterns:
    1. Never return string errors - always raise structured MCP errors
    2. Provide rich context for debugging
    3. Handle authentication requirements consistently
    4. Convert unexpected errors to proper MCP errors
    """

    @staticmethod
    def handle_validation_error(message: str, **context: Any) -> InvalidParamsError:
        """Create a standardized validation error.

        Args:
            message: Human-readable error message
            **context: Additional context for debugging

        Returns:
            InvalidParamsError with structured data
        """
        # Create base error data
        error_data = {"error_type": "validation_error", **context}

        # Add request context if available
        error_data = add_context_to_error_data(error_data)

        return InvalidParamsError(message, data=error_data)

    @staticmethod
    def handle_authentication_required(
        action: str, **context: Any
    ) -> AuthenticationRequiredError:
        """Create a standardized authentication required error.

        Args:
            action: Description of what action requires authentication
            **context: Additional context for debugging

        Returns:
            AuthenticationRequiredError with structured data
        """
        return AuthenticationRequiredError(
            action=action,
            auth_url=AUTH_VERIFICATION_URL,
            message=f"Authentication required to {action}",
        )

    @staticmethod
    def handle_unexpected_error(
        operation: str, error: Exception, **context: Any
    ) -> InternalError:
        """Convert unexpected errors to structured MCP errors.

        Args:
            operation: Description of the operation that failed
            error: The original exception
            **context: Additional context for debugging

        Returns:
            InternalError with structured data
        """
        logger.exception(f"Unexpected error in {operation}")

        # Create base error data
        error_data = {
            "error_type": "unexpected_error",
            "operation": operation,
            "original_error": str(error),
            "original_error_type": type(error).__name__,
            **context,
        }

        # Add request context if available
        error_data = add_context_to_error_data(error_data)

        return InternalError(
            f"An unexpected error occurred during {operation}", data=error_data
        )

    @staticmethod
    def handle_api_string_error(
        resource_type: str, resource_id: str, error_message: str, **context: Any
    ) -> InternalError:
        """Handle cases where API clients return error strings.

        This is a transitional method for cases where clients still return
        error strings instead of raising proper exceptions.

        Args:
            resource_type: Type of resource (movie, show, etc.)
            resource_id: ID of the resource
            error_message: Error message from API client
            **context: Additional context for debugging

        Returns:
            InternalError with structured data
        """
        # Create base error data
        error_data = {
            "error_type": "api_error",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "api_error_message": error_message,
            **context,
        }

        # Add request context if available
        error_data = add_context_to_error_data(error_data)

        return InternalError(f"Error accessing {resource_type}", data=error_data)

    @classmethod
    def with_error_handling(
        cls, operation: str, **operation_context: Any
    ) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
        """Decorator to wrap tool functions with standardized error handling.

        This decorator ensures that:
        1. MCP errors are propagated unchanged
        2. Unexpected errors are converted to structured MCP errors
        3. Operation context is preserved for debugging

        Args:
            operation: Description of the operation for error messages
            **operation_context: Context to include in error data

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                try:
                    return await func(*args, **kwargs)
                except MCPError:
                    # Let MCP errors propagate unchanged
                    raise
                except Exception as e:
                    # Convert unexpected errors to MCP errors
                    raise cls.handle_unexpected_error(
                        operation=operation,
                        error=e,
                        function=func.__name__,
                        args=sanitize_args(args) if args else None,
                        kwargs=sanitize_kwargs(kwargs) if kwargs else None,
                        **operation_context,
                    ) from e

            return wrapper

        return decorator

    @classmethod
    def validate_required_params(cls, **params: Any) -> None:
        """Validate that required parameters are provided.

        Args:
            **params: Parameter name -> value pairs to validate

        Raises:
            InvalidParamsError: If any required parameter is missing
        """
        missing: list[str] = []
        for name, value in params.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(name)

        if missing:
            raise cls.handle_validation_error(
                f"Missing required parameter(s): {', '.join(missing)}",
                missing_parameters=missing,
                provided_parameters=list(params.keys()),
            )

    @classmethod
    def validate_either_or_params(
        cls, param_sets: list[tuple[str, ...]], **params: Any
    ) -> None:
        """Validate that at least one set of alternative parameters is provided.

        Args:
            param_sets: List of parameter sets, where each set is a tuple of parameter names
            **params: Parameter name -> value pairs to validate

        Raises:
            InvalidParamsError: If no valid parameter set is provided
        """
        for param_set in param_sets:
            if all(
                (value := params.get(param)) is not None
                and (not isinstance(value, str) or (value and value.strip()))
                for param in param_set
            ):
                return  # Found a valid set

        # No valid set found
        param_descriptions = [" and ".join(param_set) for param_set in param_sets]
        raise cls.handle_validation_error(
            f"Must provide one of: {' OR '.join(param_descriptions)}",
            required_parameter_sets=param_sets,
            provided_parameters={k: v for k, v in params.items() if v is not None},
        )
