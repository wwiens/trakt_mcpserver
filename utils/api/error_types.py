"""Enhanced error types for Trakt MCP server with rich context and MCP compliance."""

from typing import Any

from utils.api.errors import InvalidParamsError, InvalidRequestError, MCPError


class TraktAPIError(MCPError):
    """Base class for Trakt API-specific errors with rich context.

    Provides enhanced error information including endpoint context,
    request parameters, and correlation IDs for better debugging.
    """

    def __init__(
        self,
        code: int,
        message: str,
        data: dict[str, Any] | None = None,
        *,
        endpoint: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        correlation_id: str | None = None,
        http_status: int | None = None,
    ) -> None:
        """Initialize Trakt API error with rich context.

        Args:
            code: Standard JSON-RPC error code
            message: Human-readable error message
            data: Optional additional error data
            endpoint: API endpoint that failed
            resource_type: Type of resource (show, movie, user, etc.)
            resource_id: ID of the resource being accessed
            correlation_id: Request correlation ID for tracing
            http_status: HTTP status code from API response
        """
        enhanced_data = data or {}

        # Add context information
        if endpoint is not None:
            enhanced_data["endpoint"] = endpoint
        if resource_type is not None:
            enhanced_data["resource_type"] = resource_type
        if resource_id is not None:
            enhanced_data["resource_id"] = resource_id
        if correlation_id is not None:
            enhanced_data["correlation_id"] = correlation_id
        if http_status is not None:
            enhanced_data["http_status"] = http_status

        super().__init__(code, message, enhanced_data)


class AuthenticationRequiredError(InvalidRequestError):
    """Raised when authentication is required but not provided.

    This error should be used when a user attempts to access
    a protected resource without valid authentication.
    """

    def __init__(
        self,
        action: str,
        auth_url: str = "https://trakt.tv/pin/346",
        message: str | None = None,
    ) -> None:
        """Initialize authentication required error.

        Args:
            action: The action that requires authentication
            auth_url: URL for user to complete authentication
            message: Optional custom message (defaults to standard message)
        """
        if message is None:
            message = f"Authentication required to {action}"

        super().__init__(
            message,
            data={
                "error_type": "auth_required",
                "auth_url": auth_url,
                "action": action,
                "instructions": (
                    "Please complete authentication at the provided URL, "
                    "then check authorization status."
                ),
            },
        )


class AuthorizationPendingError(MCPError):
    """Raised when device authorization is pending user approval.

    This is a special case error used during OAuth device flow
    when the user hasn't yet approved the device code.
    """

    def __init__(
        self, device_code: str | None = None, expires_in: int | None = None
    ) -> None:
        """Initialize authorization pending error.

        Args:
            device_code: The device code waiting for authorization
            expires_in: Seconds until device code expires
        """
        data: dict[str, Any] = {"error_type": "auth_pending"}
        if device_code is not None:
            data["device_code"] = device_code
        if expires_in is not None:
            data["expires_in"] = expires_in

        super().__init__(
            code=-32001,  # Custom code for pending auth
            message="Authorization pending. User must approve device code.",
            data=data,
        )


class TraktValidationError(InvalidParamsError):
    """Raised when request parameters fail validation.

    Provides detailed information about which parameters
    are invalid and why.
    """

    def __init__(
        self,
        message: str,
        *,
        invalid_params: list[str] | None = None,
        missing_params: list[str] | None = None,
        validation_details: dict[str, str] | None = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Human-readable error message
            invalid_params: List of invalid parameter names
            missing_params: List of missing required parameter names
            validation_details: Detailed validation error messages per parameter
        """
        data: dict[str, Any] = {"error_type": "validation_error"}

        if invalid_params:
            data["invalid_params"] = invalid_params
        if missing_params:
            data["missing_params"] = missing_params
        if validation_details:
            data["validation_details"] = validation_details

        super().__init__(message, data)


class TraktResourceNotFoundError(TraktAPIError):
    """Raised when a requested Trakt resource is not found.

    Provides context about what resource was being accessed.
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: str | None = None,
        **context: Any,
    ) -> None:
        """Initialize resource not found error.

        Args:
            resource_type: Type of resource (show, movie, user, etc.)
            resource_id: ID of the resource that wasn't found
            message: Optional custom message
            **context: Additional context information
        """
        if message is None:
            message = f"The requested {resource_type} '{resource_id}' was not found"

        super().__init__(
            code=-32600,  # Invalid request
            message=message,
            resource_type=resource_type,
            resource_id=resource_id,
            http_status=404,
            **context,
        )


class TraktRateLimitError(TraktAPIError):
    """Raised when Trakt API rate limit is exceeded.

    Includes information about retry timing.
    """

    def __init__(
        self,
        retry_after: int | None = None,
        message: str | None = None,
        **context: Any,
    ) -> None:
        """Initialize rate limit error.

        Args:
            retry_after: Seconds to wait before retrying
            message: Optional custom message
            **context: Additional context information
        """
        if message is None:
            if retry_after:
                message = f"Rate limit exceeded. Please retry in {retry_after} seconds."
            else:
                message = "Rate limit exceeded. Please try again later."

        data = {"retry_after": retry_after}

        super().__init__(
            code=-32600,  # Invalid request
            message=message,
            data=data,
            http_status=429,
            **context,
        )


class TraktServerError(TraktAPIError):
    """Raised when Trakt API server encounters an error.

    Used for 5xx status codes from the API.
    """

    def __init__(
        self,
        http_status: int,
        message: str | None = None,
        is_temporary: bool = True,
        **context: Any,
    ) -> None:
        """Initialize server error.

        Args:
            http_status: HTTP status code (5xx)
            message: Optional custom message
            is_temporary: Whether the error is likely temporary
            **context: Additional context information
        """
        if message is None:
            if http_status == 502:
                message = "Bad gateway. The Trakt API server is experiencing issues."
            elif http_status == 503:
                message = "Service unavailable. Please try again in 30 seconds."
            else:
                message = f"Trakt API server error (HTTP {http_status})"

        super().__init__(
            code=-32603,  # Internal error
            message=message,
            data={"is_temporary": is_temporary},
            http_status=http_status,
            **context,
        )
