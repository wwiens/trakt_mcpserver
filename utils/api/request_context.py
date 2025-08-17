"""Request context management for Trakt MCP server.

This module provides request context tracking including correlation IDs,
endpoint information, and request parameters for enhanced debugging.
"""

import time
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from typing import Any


@dataclass
class RequestContext:
    """Request context for tracking request information across the application.

    This class holds contextual information about the current request including
    correlation ID, endpoint details, timing information, and request parameters.
    """

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    endpoint: str | None = None
    method: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    user_id: str | None = None
    parameters: dict[str, Any] = field(default_factory=lambda: {})
    start_time: float = field(default_factory=time.time)

    def with_endpoint(self, endpoint: str, method: str = "GET") -> "RequestContext":
        """Create a new context with endpoint information.

        Args:
            endpoint: API endpoint being accessed
            method: HTTP method being used

        Returns:
            New RequestContext with endpoint information
        """
        return replace(self, endpoint=endpoint, method=method)

    def with_resource(self, resource_type: str, resource_id: str) -> "RequestContext":
        """Create a new context with resource information.

        Args:
            resource_type: Type of resource (show, movie, user, etc.)
            resource_id: ID of the resource being accessed

        Returns:
            New RequestContext with resource information
        """
        return replace(self, resource_type=resource_type, resource_id=resource_id)

    def with_parameters(self, **params: Any) -> "RequestContext":
        """Create a new context with additional parameters.

        Args:
            **params: Additional parameters to add to context

        Returns:
            New RequestContext with merged parameters
        """
        new_params = self.parameters.copy()
        new_params.update(params)
        return replace(self, parameters=new_params)

    def with_user(self, user_id: str) -> "RequestContext":
        """Create a new context with user information.

        Args:
            user_id: ID of the authenticated user

        Returns:
            New RequestContext with user information
        """
        return replace(self, user_id=user_id)

    def elapsed_time(self) -> float:
        """Get elapsed time since request started."""
        return time.time() - self.start_time

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for logging and error data.

        Returns:
            Dictionary representation of the context
        """
        return {
            "correlation_id": self.correlation_id,
            "endpoint": self.endpoint,
            "method": self.method,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "parameters": self.parameters,
            "elapsed_time": self.elapsed_time(),
        }


# Context variable for request-scoped context
_request_context: ContextVar[RequestContext | None] = ContextVar(
    "request_context", default=None
)


def get_current_context() -> RequestContext | None:
    """Get the current request context.

    Returns:
        Current RequestContext or None if not set
    """
    return _request_context.get()


def set_current_context(context: RequestContext) -> None:
    """Set the current request context.

    Args:
        context: RequestContext to set as current
    """
    _request_context.set(context)


def clear_current_context() -> None:
    """Clear the current request context."""
    _request_context.set(None)


def create_new_context() -> RequestContext:
    """Create a new request context with a unique correlation ID.

    Returns:
        New RequestContext instance
    """
    return RequestContext()


def get_correlation_id() -> str | None:
    """Get the correlation ID from the current context.

    Returns:
        Correlation ID or None if no context is set
    """
    context = get_current_context()
    return context.correlation_id if context else None


def add_context_to_error_data(error_data: dict[str, Any]) -> dict[str, Any]:
    """Add current request context to error data.

    Args:
        error_data: Existing error data dictionary

    Returns:
        Error data with context information added (always a copy)
    """
    context = get_current_context()
    # Always create a copy to avoid modifying the original
    enhanced_data = error_data.copy()

    if context:
        # Use nested structure to avoid key collisions
        enhanced_data["request_context"] = context.to_dict()

    return enhanced_data
