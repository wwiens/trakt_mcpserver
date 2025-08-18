"""Tests for structured logging functionality."""

import json
import logging
import time
from io import StringIO
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from tests.types_stub import LogRecordExtended

from utils.api.request_context import (
    RequestContext,
    clear_current_context,
    set_current_context,
)
from utils.api.structured_logging import (
    ContextFilter,
    StructuredFormatter,
    get_structured_logger,
    log_api_request,
    log_api_response,
    log_error_with_context,
    performance_timer,
    setup_structured_logging,
)


def test_context_filter_with_context():
    """Test ContextFilter adds context information to log records."""
    # Set up context
    context = (
        RequestContext()
        .with_endpoint("/test/endpoint", "GET")
        .with_resource("test", "test-id")
        .with_user("user123")
    )
    set_current_context(context)

    # Create log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Apply filter
    filter_instance = ContextFilter()
    result = filter_instance.filter(record)

    # Check filter returns True
    assert result is True

    # Cast to extended type for dynamic attributes
    extended_record = cast("LogRecordExtended", record)

    # Check context information was added
    assert extended_record.correlation_id == context.correlation_id
    assert extended_record.endpoint == "/test/endpoint"
    assert extended_record.method == "GET"
    assert extended_record.resource_type == "test"
    assert extended_record.resource_id == "test-id"
    assert extended_record.user_id == "user123"
    assert extended_record.elapsed_time is not None


def test_context_filter_without_context():
    """Test ContextFilter handles missing context gracefully."""
    # Clear context
    clear_current_context()

    # Create log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Apply filter
    filter_instance = ContextFilter()
    result = filter_instance.filter(record)

    # Check filter returns True
    assert result is True

    # Cast to extended type for dynamic attributes
    extended_record = cast("LogRecordExtended", record)

    # Check defaults were set
    assert extended_record.correlation_id is None
    assert extended_record.endpoint is None
    assert extended_record.method is None
    assert extended_record.resource_type is None
    assert extended_record.resource_id is None
    assert extended_record.user_id is None
    assert extended_record.elapsed_time is None


def test_structured_formatter_basic():
    """Test StructuredFormatter produces valid JSON."""
    # Create log record
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Cast to extended type for dynamic attributes
    extended_record = cast("LogRecordExtended", record)

    # Add context fields
    extended_record.correlation_id = "test-correlation-id"
    extended_record.endpoint = "/test/endpoint"
    extended_record.method = "GET"

    # Format the record (using original record for formatter)
    formatter = StructuredFormatter()
    formatted = formatter.format(record)

    # Parse as JSON
    log_data = json.loads(formatted)

    # Check required fields
    assert "timestamp" in log_data
    assert log_data["level"] == "INFO"
    assert log_data["logger"] == "test.logger"
    assert log_data["message"] == "Test message"
    assert log_data["correlation_id"] == "test-correlation-id"
    assert log_data["endpoint"] == "/test/endpoint"
    assert log_data["method"] == "GET"


def test_structured_formatter_with_exception():
    """Test StructuredFormatter handles exceptions."""
    import sys

    # Create log record with exception
    try:
        raise ValueError("Test error")
    except ValueError:
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error occurred",
            args=(),
            exc_info=sys.exc_info(),
        )

    # Format the record
    formatter = StructuredFormatter()
    formatted = formatter.format(record)

    # Parse as JSON
    log_data = json.loads(formatted)

    # Check exception information is included
    assert "exception" in log_data
    assert "ValueError: Test error" in log_data["exception"]


def test_structured_formatter_with_extra_fields():
    """Test StructuredFormatter includes extra fields."""
    # Create log record
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Cast to extended type for dynamic attributes
    extended_record = cast("LogRecordExtended", record)

    # Add extra fields
    extended_record.custom_field = "custom_value"
    extended_record.operation = "test_operation"

    # Format the record
    formatter = StructuredFormatter()
    formatted = formatter.format(record)

    # Parse as JSON
    log_data = json.loads(formatted)

    # Check extra fields are included
    assert log_data["custom_field"] == "custom_value"
    assert log_data["operation"] == "test_operation"


def test_setup_structured_logging():
    """Test structured logging setup."""
    logger_name = "test.structured"
    logger = setup_structured_logging(logger_name, logging.DEBUG)

    # Check logger configuration
    assert logger.name == logger_name
    assert logger.level == logging.DEBUG
    assert logger.propagate is False
    assert len(logger.handlers) == 1

    # Check handler configuration
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert isinstance(handler.formatter, StructuredFormatter)
    assert any(isinstance(f, ContextFilter) for f in handler.filters)


def test_get_structured_logger_new():
    """Test getting a new structured logger."""
    logger_name = "test.new.logger"
    logger = get_structured_logger(logger_name)

    # Check logger has structured formatting
    assert len(logger.handlers) >= 1
    handler = logger.handlers[0]
    assert isinstance(handler.formatter, StructuredFormatter)


def test_get_structured_logger_existing():
    """Test getting an existing structured logger."""
    logger_name = "test.existing.logger"

    # First call sets up structured logging
    logger1 = get_structured_logger(logger_name)
    original_handler_count = len(logger1.handlers)

    # Second call should return same logger without adding handlers
    logger2 = get_structured_logger(logger_name)

    assert logger1 is logger2
    assert len(logger2.handlers) == original_handler_count


def test_performance_timer():
    """Test performance timer context manager."""
    # Capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(StructuredFormatter())

    logger = logging.getLogger("test.performance")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Use performance timer
    operation_name = "test_operation"
    with performance_timer(operation_name, logger):
        time.sleep(0.01)  # Small delay

    # Check log output
    log_output = log_stream.getvalue()
    log_lines = [line for line in log_output.strip().split("\n") if line]

    # Should have start and complete messages
    assert len(log_lines) >= 2

    # Parse log entries
    start_log = json.loads(log_lines[0])
    complete_log = json.loads(log_lines[-1])

    # Check start log
    assert start_log["operation"] == operation_name
    assert start_log["event"] == "operation_start"

    # Check complete log
    assert complete_log["operation"] == operation_name
    assert complete_log["event"] == "operation_complete"
    assert "duration" in complete_log
    assert "duration_ms" in complete_log
    assert complete_log["duration"] > 0


def test_log_api_request():
    """Test API request logging."""
    # Capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(StructuredFormatter())

    logger = logging.getLogger("test.api.request")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Log API request
    endpoint = "/test/endpoint"
    method = "POST"
    parameters = {"param1": "value1", "param2": 42}

    log_api_request(endpoint, method, parameters, logger)

    # Check log output
    log_output = log_stream.getvalue().strip()
    log_data = json.loads(log_output)

    # Check log content
    assert log_data["event"] == "api_request"
    assert log_data["endpoint"] == endpoint
    assert log_data["method"] == method
    assert log_data["parameters"] == parameters
    assert f"API request: {method} {endpoint}" in log_data["message"]


def test_log_api_response():
    """Test API response logging."""
    # Capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(StructuredFormatter())

    logger = logging.getLogger("test.api.response")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Log API response
    endpoint = "/test/endpoint"
    status_code = 200
    response_size = 1024

    log_api_response(endpoint, status_code, response_size, logger)

    # Check log output
    log_output = log_stream.getvalue().strip()
    log_data = json.loads(log_output)

    # Check log content
    assert log_data["event"] == "api_response"
    assert log_data["endpoint"] == endpoint
    assert log_data["status_code"] == status_code
    assert log_data["response_size"] == response_size
    assert f"API response: {endpoint}" in log_data["message"]


def test_log_error_with_context():
    """Test error logging with context."""
    # Capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(StructuredFormatter())

    logger = logging.getLogger("test.error")
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)

    # Log error
    error_message = "Test error occurred"
    error = ValueError("Test exception")
    operation = "test_operation"

    log_error_with_context(error_message, error, operation, logger)

    # Check log output
    log_output = log_stream.getvalue().strip()
    log_data = json.loads(log_output)

    # Check log content
    assert log_data["event"] == "error"
    assert log_data["error_type"] == "ValueError"
    assert log_data["error_message"] == "Test exception"
    assert log_data["operation"] == operation
    assert log_data["message"] == error_message
    assert log_data["level"] == "ERROR"


def test_performance_timer_with_default_logger():
    """Test performance timer with default logger."""
    operation_name = "test_default_logger"

    # Should not raise any exceptions
    with performance_timer(operation_name):
        time.sleep(0.001)  # Very small delay


def test_log_api_request_with_default_logger():
    """Test API request logging with default logger."""
    endpoint = "/test/default"

    # Should not raise any exceptions
    log_api_request(endpoint)


def test_log_api_response_with_default_logger():
    """Test API response logging with default logger."""
    endpoint = "/test/default"

    # Should not raise any exceptions
    log_api_response(endpoint)


def test_log_error_with_default_logger():
    """Test error logging with default logger."""
    error = Exception("Test error")

    # Should not raise any exceptions
    log_error_with_context("Test message", error)


def teardown_function():
    """Clean up after each test."""
    clear_current_context()

    # Clean up loggers to avoid interference
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("test."):
            logger = logging.getLogger(name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
