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
                        args=str(args) if args else None,
                        kwargs=str(kwargs) if kwargs else None,
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
