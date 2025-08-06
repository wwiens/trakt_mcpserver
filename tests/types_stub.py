"""Type stubs for test utilities."""

import logging
from typing import Any, Protocol

from models.types import DeviceCodeResponse


class LogRecordExtended(logging.LogRecord):
    """Extended LogRecord with custom attributes for structured logging.

    This extends the standard LogRecord to include custom attributes
    that are dynamically added by our ContextFilter and test code.
    """

    correlation_id: str | None
    request_context: dict[str, Any] | None
    endpoint: str | None
    method: str | None
    resource_type: str | None
    resource_id: str | None
    user_id: str | None
    elapsed_time: float | None

    # Additional attributes used in tests
    custom_field: str | None
    operation: str | None
    event: str | None
    duration: float | None
    duration_ms: float | None
    parameters: dict[str, Any] | None
    status_code: int | None
    response_size: int | None
    error_type: str | None
    error_message: str | None


class MockClientProtocol(Protocol):
    """Protocol for mock client objects in tests."""

    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        ...

    def clear_auth(self) -> None:
        """Clear authentication."""
        ...


class MockAuthClientProtocol(MockClientProtocol, Protocol):
    """Protocol for mock authentication clients in tests."""

    async def get_device_code(self) -> DeviceCodeResponse:
        """Get OAuth device code."""
        ...

    async def get_device_token(self, device_code: str) -> dict[str, Any]:
        """Poll for device token."""
        ...


class MockTraktAPIResponse(Protocol):
    """Protocol for mock Trakt API responses in tests."""

    status_code: int
    headers: dict[str, str]
    json: Any
    text: str


class MCPErrorData(Protocol):
    """Protocol for MCP error data dictionary."""

    def __getitem__(self, key: str) -> Any:
        """Support dictionary access for error data."""
        ...

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for error data."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Support .get() method for error data."""
        ...


class MCPErrorWithData(Protocol):
    """Protocol for MCP errors that have data attribute."""

    data: MCPErrorData
    code: int
    message: str
