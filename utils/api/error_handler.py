"""Centralized error handler for Trakt API responses."""

import contextlib
import logging
import uuid
from collections.abc import Callable
from typing import Any

import httpx

from utils.api.errors import (
    InternalError,
    InvalidParamsError,
    InvalidRequestError,
    MCPError,
)

from .error_types import (
    AuthenticationRequiredError,
    AuthorizationPendingError,
    TraktRateLimitError,
    TraktResourceNotFoundError,
    TraktServerError,
    TraktValidationError,
)

logger = logging.getLogger("trakt_mcp.error_handler")


class TraktAPIErrorHandler:
    """Centralized handler for Trakt API errors.

    Converts HTTP errors from the Trakt API into appropriate
    MCP-compliant errors with rich context and proper logging.
    """

    @classmethod
    def handle_http_error(
        cls,
        error: httpx.HTTPStatusError,
        *,
        endpoint: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        correlation_id: str | None = None,
    ) -> MCPError:
        """Convert HTTP error to appropriate MCP error.

        Args:
            error: The HTTP error from the API call
            endpoint: API endpoint that failed
            resource_type: Type of resource being accessed
            resource_id: ID of the resource being accessed
            correlation_id: Request correlation ID for tracing

        Returns:
            Appropriate MCPError subclass for the HTTP status code
        """
        status_code = error.response.status_code

        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        # Extract response details for context
        try:
            response_text = error.response.text
        except Exception:
            response_text = "Unable to read response text"

        # Log the error with context
        cls.log_http_error(
            status_code=status_code,
            endpoint=endpoint,
            resource_type=resource_type,
            resource_id=resource_id,
            correlation_id=correlation_id,
            response_text=response_text,
        )

        # Get appropriate handler for status code
        handler = cls.get_status_code_handler(status_code)

        # Call handler with context
        return handler(
            error=error,
            endpoint=endpoint,
            resource_type=resource_type,
            resource_id=resource_id,
            correlation_id=correlation_id,
            response_text=response_text,
        )

    @classmethod
    def get_status_code_handler(cls, status_code: int) -> Callable[..., MCPError]:
        """Get the appropriate handler method for a status code."""
        handlers = {
            400: cls.handle_bad_request,
            401: cls.handle_unauthorized,
            403: cls.handle_forbidden,
            404: cls.handle_not_found,
            409: cls.handle_conflict,
            422: cls.handle_validation_error,
            429: cls.handle_rate_limit,
            500: cls.handle_server_error,
            502: cls.handle_bad_gateway,
            503: cls.handle_service_unavailable,
        }

        return handlers.get(status_code, cls.handle_unknown_error)

    @classmethod
    def handle_bad_request(
        cls, **context: Any
    ) -> InvalidParamsError | AuthorizationPendingError | TraktValidationError:
        """Handle 400 Bad Request errors."""
        response_text = context.get("response_text", "")

        # Check for authorization pending (OAuth device flow)
        if "authorization_pending" in response_text.lower():
            return AuthorizationPendingError(
                device_code=context.get("resource_id"),
            )

        # Check for specific validation errors
        if "invalid" in response_text.lower() or "validation" in response_text.lower():
            return TraktValidationError(
                "Bad request. Please check your request parameters.",
                validation_details={"api_response": response_text},
            )

        return InvalidParamsError(
            "Bad request. Please check your request parameters.",
            data={
                "http_status": 400,
                "details": response_text,
                "endpoint": context.get("endpoint"),
                "correlation_id": context.get("correlation_id"),
            },
        )

    @classmethod
    def handle_unauthorized(cls, **context: Any) -> AuthenticationRequiredError:
        """Handle 401 Unauthorized errors."""
        resource_type = context.get("resource_type") or "resource"
        action = f"access {resource_type}"

        return AuthenticationRequiredError(
            action=action,
            message="Authentication required. Please check your Trakt API credentials.",
        )

    @classmethod
    def handle_forbidden(cls, **context: Any) -> InvalidRequestError:
        """Handle 403 Forbidden errors."""
        return InvalidRequestError(
            "Forbidden. Invalid API key or unapproved application.",
            data={
                "http_status": 403,
                "endpoint": context.get("endpoint"),
                "correlation_id": context.get("correlation_id"),
                "details": context.get("response_text"),
            },
        )

    @classmethod
    def handle_not_found(cls, **context: Any) -> TraktResourceNotFoundError:
        """Handle 404 Not Found errors."""
        resource_type = context.get("resource_type") or "resource"
        resource_id = context.get("resource_id") or "unknown"

        return TraktResourceNotFoundError(
            resource_type=resource_type,
            resource_id=resource_id,
            endpoint=context.get("endpoint"),
            correlation_id=context.get("correlation_id"),
        )

    @classmethod
    def handle_conflict(cls, **context: Any) -> InvalidRequestError:
        """Handle 409 Conflict errors."""
        return InvalidRequestError(
            "Conflict. The resource already exists or cannot be modified.",
            data={
                "http_status": 409,
                "endpoint": context.get("endpoint"),
                "resource_type": context.get("resource_type"),
                "resource_id": context.get("resource_id"),
                "correlation_id": context.get("correlation_id"),
                "details": context.get("response_text"),
            },
        )

    @classmethod
    def handle_validation_error(cls, **context: Any) -> TraktValidationError:
        """Handle 422 Unprocessable Entity errors."""
        response_text = context.get("response_text", "")

        validation_details: dict[str, str] = {"api_response": response_text}

        endpoint = context.get("endpoint")
        if endpoint is not None:
            validation_details["endpoint"] = endpoint

        correlation_id = context.get("correlation_id")
        if correlation_id is not None:
            validation_details["correlation_id"] = correlation_id

        return TraktValidationError(
            "Validation error. Please check your input data.",
            validation_details=validation_details,
        )

    @classmethod
    def handle_rate_limit(cls, **context: Any) -> TraktRateLimitError:
        """Handle 429 Rate Limit Exceeded errors."""
        # Try to extract retry-after header if available
        error = context.get("error")
        retry_after = None

        if error and hasattr(error, "response"):
            retry_after_header = error.response.headers.get("retry-after")
            if retry_after_header:
                with contextlib.suppress(ValueError):
                    retry_after = int(retry_after_header)

        return TraktRateLimitError(
            retry_after=retry_after,
            endpoint=context.get("endpoint"),
            correlation_id=context.get("correlation_id"),
        )

    @classmethod
    def handle_server_error(cls, **context: Any) -> TraktServerError:
        """Handle 500 Internal Server Error."""
        return TraktServerError(
            http_status=500,
            message="Trakt API server error. Please try again later.",
            endpoint=context.get("endpoint"),
            correlation_id=context.get("correlation_id"),
        )

    @classmethod
    def handle_bad_gateway(cls, **context: Any) -> TraktServerError:
        """Handle 502 Bad Gateway errors."""
        return TraktServerError(
            http_status=502,
            message="Bad gateway. The Trakt API server is experiencing issues.",
            endpoint=context.get("endpoint"),
            correlation_id=context.get("correlation_id"),
        )

    @classmethod
    def handle_service_unavailable(cls, **context: Any) -> TraktServerError:
        """Handle 503 Service Unavailable errors."""
        return TraktServerError(
            http_status=503,
            message="Service unavailable. Please try again in 30 seconds.",
            endpoint=context.get("endpoint"),
            correlation_id=context.get("correlation_id"),
        )

    @classmethod
    def handle_unknown_error(cls, **context: Any) -> InternalError:
        """Handle unknown/unmapped status codes."""
        error = context.get("error")
        status_code = error.response.status_code if error else "unknown"

        return InternalError(
            f"HTTP {status_code} error occurred",
            data={
                "http_status": status_code,
                "endpoint": context.get("endpoint"),
                "resource_type": context.get("resource_type"),
                "resource_id": context.get("resource_id"),
                "correlation_id": context.get("correlation_id"),
                "response": context.get("response_text"),
            },
        )

    @classmethod
    def log_http_error(
        cls,
        *,
        status_code: int,
        endpoint: str | None,
        resource_type: str | None,
        resource_id: str | None,
        correlation_id: str,
        response_text: str,
    ) -> None:
        """Log HTTP error with structured context."""
        log_context = {
            "http_status": status_code,
            "correlation_id": correlation_id,
            "response_length": len(response_text),
        }

        if endpoint:
            log_context["endpoint"] = endpoint
        if resource_type:
            log_context["resource_type"] = resource_type
        if resource_id:
            log_context["resource_id"] = resource_id

        # Truncate response text for logging
        truncated_response = (
            response_text[:200] + "..." if len(response_text) > 200 else response_text
        )
        log_context["response_preview"] = truncated_response

        logger.error(
            f"Trakt API HTTP {status_code} error",
            extra={"context": log_context},
        )


def create_correlation_id() -> str:
    """Generate a new correlation ID for request tracing."""
    return str(uuid.uuid4())
