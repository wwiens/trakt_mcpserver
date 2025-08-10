"""Structured logging utilities for the Trakt MCP server.

This module provides structured logging capabilities with request context,
correlation IDs, and performance metrics.
"""

import json
import logging
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from .request_context import get_current_context


class LogRecordExtended(logging.LogRecord):
    """Extended LogRecord with custom attributes for structured logging."""

    correlation_id: str | None
    request_context: dict[str, Any] | None
    endpoint: str | None
    method: str | None
    resource_type: str | None
    resource_id: str | None
    user_id: str | None
    elapsed_time: float | None


class ContextFilter(logging.Filter):
    """Logging filter that adds request context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request context information to the log record.

        Args:
            record: The log record to enhance

        Returns:
            True to include the record in output
        """
        context = get_current_context()
        if context:
            # Add context information to the record
            record.correlation_id = context.correlation_id
            record.endpoint = context.endpoint
            record.method = context.method
            record.resource_type = context.resource_type
            record.resource_id = context.resource_id
            record.user_id = context.user_id
            record.elapsed_time = context.elapsed_time()
        else:
            # Set defaults when no context is available
            record.correlation_id = None
            record.endpoint = None
            record.method = None
            record.resource_type = None
            record.resource_id = None
            record.user_id = None
            record.elapsed_time = None

        return True


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for log records."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as structured JSON.

        Args:
            record: The log record to format

        Returns:
            JSON-formatted log entry
        """
        # Create base log entry
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context information if available using type-safe approach
        # Note: We can safely treat record as extended since ContextFilter adds the attributes

        correlation_id = getattr(record, "correlation_id", None)
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        endpoint = getattr(record, "endpoint", None)
        if endpoint:
            log_entry["endpoint"] = endpoint

        method = getattr(record, "method", None)
        if method:
            log_entry["method"] = method

        resource_type = getattr(record, "resource_type", None)
        if resource_type:
            log_entry["resource_type"] = resource_type

        resource_id = getattr(record, "resource_id", None)
        if resource_id:
            log_entry["resource_id"] = resource_id

        user_id = getattr(record, "user_id", None)
        if user_id:
            log_entry["user_id"] = user_id

        elapsed_time = getattr(record, "elapsed_time", None)
        if elapsed_time is not None:
            log_entry["elapsed_time"] = float(elapsed_time)

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            extra_fields = getattr(record, "extra_fields", None)
            if extra_fields:
                log_entry.update(extra_fields)

        # Add fields from LoggerAdapter's extra
        if hasattr(record, "__dict__"):
            # Add any extra fields not already included
            for key, value in record.__dict__.items():
                if (
                    key not in log_entry
                    and not key.startswith("_")
                    and key
                    not in [
                        "name",
                        "msg",
                        "args",
                        "levelname",
                        "levelno",
                        "pathname",
                        "filename",
                        "module",
                        "lineno",
                        "funcName",
                        "created",
                        "msecs",
                        "relativeCreated",
                        "thread",
                        "threadName",
                        "processName",
                        "process",
                        "getMessage",
                        "exc_info",
                        "exc_text",
                        "stack_info",
                    ]
                ):
                    log_entry[key] = value

        return json.dumps(log_entry, default=str)


def setup_structured_logging(
    logger_name: str = "trakt_mcp", level: int = logging.INFO
) -> logging.Logger:
    """Set up structured logging for the application.

    Args:
        logger_name: Name of the logger to configure
        level: Logging level

    Returns:
        Configured logger with structured formatting
    """
    logger = logging.getLogger(logger_name)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with structured formatter
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Add context filter and structured formatter
    handler.addFilter(ContextFilter())
    handler.setFormatter(StructuredFormatter())

    logger.addHandler(handler)
    logger.setLevel(level)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


def get_structured_logger(name: str) -> logging.Logger:
    """Get a logger with structured formatting.

    Args:
        name: Logger name

    Returns:
        Logger configured for structured output
    """
    logger = logging.getLogger(name)

    # If not already configured, set up structured logging
    if not any(
        isinstance(handler.formatter, StructuredFormatter)
        for handler in logger.handlers
    ):
        return setup_structured_logging(name)

    return logger


@contextmanager
def performance_timer(
    operation: str, logger: logging.Logger | None = None
) -> Generator[None, None, None]:
    """Context manager for timing operations with structured logging.

    Args:
        operation: Name of the operation being timed
        logger: Logger to use (defaults to structured logger)

    Yields:
        None
    """
    if logger is None:
        logger = get_structured_logger("trakt_mcp.performance")

    start_time = time.time()

    try:
        logger.info(
            f"Starting {operation}",
            extra={"operation": operation, "event": "operation_start"},
        )
        yield
    finally:
        elapsed = time.time() - start_time
        logger.info(
            f"Completed {operation}",
            extra={
                "operation": operation,
                "event": "operation_complete",
                "duration": elapsed,
                "duration_ms": elapsed * 1000,
            },
        )


def log_api_request(
    endpoint: str,
    method: str = "GET",
    parameters: dict[str, Any] | None = None,
    logger: logging.Logger | None = None,
) -> None:
    """Log API request with structured information.

    Args:
        endpoint: API endpoint being called
        method: HTTP method
        parameters: Request parameters
        logger: Logger to use (defaults to structured logger)
    """
    if logger is None:
        logger = get_structured_logger("trakt_mcp.api")

    extra_fields: dict[str, Any] = {
        "event": "api_request",
        "endpoint": endpoint,
        "method": method,
    }

    if parameters:
        extra_fields["parameters"] = parameters

    logger.info(f"API request: {method} {endpoint}", extra=extra_fields)


def log_api_response(
    endpoint: str,
    status_code: int | None = None,
    response_size: int | None = None,
    logger: logging.Logger | None = None,
) -> None:
    """Log API response with structured information.

    Args:
        endpoint: API endpoint that responded
        status_code: HTTP status code
        response_size: Size of response in bytes
        logger: Logger to use (defaults to structured logger)
    """
    if logger is None:
        logger = get_structured_logger("trakt_mcp.api")

    extra_fields: dict[str, Any] = {"event": "api_response", "endpoint": endpoint}

    if status_code is not None:
        extra_fields["status_code"] = status_code
    if response_size is not None:
        extra_fields["response_size"] = response_size

    logger.info(f"API response: {endpoint}", extra=extra_fields)


def log_error_with_context(
    message: str,
    error: Exception,
    operation: str | None = None,
    logger: logging.Logger | None = None,
) -> None:
    """Log error with full context information.

    Args:
        message: Error message
        error: Exception that occurred
        operation: Operation that failed
        logger: Logger to use (defaults to structured logger)
    """
    if logger is None:
        logger = get_structured_logger("trakt_mcp.error")

    extra_fields = {
        "event": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if operation:
        extra_fields["operation"] = operation

    logger.error(message, extra=extra_fields, exc_info=True)
