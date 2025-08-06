"""Tests for request context functionality."""

import time
import uuid

import pytest

from utils.api.request_context import (
    RequestContext,
    add_context_to_error_data,
    clear_current_context,
    create_new_context,
    get_correlation_id,
    get_current_context,
    set_current_context,
)


def test_request_context_creation():
    """Test basic RequestContext creation."""
    context = RequestContext()

    # Check that correlation_id is generated
    assert context.correlation_id is not None
    assert len(context.correlation_id) > 0

    # Check defaults
    assert context.endpoint is None
    assert context.method is None
    assert context.resource_type is None
    assert context.resource_id is None
    assert context.user_id is None
    assert context.parameters == {}

    # Check start_time is set
    assert context.start_time is not None
    assert isinstance(context.start_time, float)


def test_request_context_with_endpoint():
    """Test adding endpoint information to context."""
    context = RequestContext()
    new_context = context.with_endpoint("/shows/trending", "GET")

    # Original context unchanged
    assert context.endpoint is None
    assert context.method is None

    # New context has endpoint info
    assert new_context.endpoint == "/shows/trending"
    assert new_context.method == "GET"

    # Correlation ID is preserved
    assert new_context.correlation_id == context.correlation_id


def test_request_context_with_resource():
    """Test adding resource information to context."""
    context = RequestContext()
    new_context = context.with_resource("show", "breaking-bad")

    # Original context unchanged
    assert context.resource_type is None
    assert context.resource_id is None

    # New context has resource info
    assert new_context.resource_type == "show"
    assert new_context.resource_id == "breaking-bad"

    # Correlation ID is preserved
    assert new_context.correlation_id == context.correlation_id


def test_request_context_with_parameters():
    """Test adding parameters to context."""
    context = RequestContext()
    new_context = context.with_parameters(limit=10, period="weekly")

    # Original context unchanged
    assert context.parameters == {}

    # New context has parameters
    assert new_context.parameters == {"limit": 10, "period": "weekly"}

    # Correlation ID is preserved
    assert new_context.correlation_id == context.correlation_id


def test_request_context_with_user():
    """Test adding user information to context."""
    context = RequestContext()
    new_context = context.with_user("user123")

    # Original context unchanged
    assert context.user_id is None

    # New context has user info
    assert new_context.user_id == "user123"

    # Correlation ID is preserved
    assert new_context.correlation_id == context.correlation_id


def test_request_context_chaining():
    """Test chaining context modifications."""
    context = RequestContext()

    final_context = (
        context.with_endpoint("/shows/search", "GET")
        .with_resource("show", "breaking-bad")
        .with_parameters(query="breaking")
        .with_user("user123")
    )

    # Final context has all information
    assert final_context.endpoint == "/shows/search"
    assert final_context.method == "GET"
    assert final_context.resource_type == "show"
    assert final_context.resource_id == "breaking-bad"
    assert final_context.parameters == {"query": "breaking"}
    assert final_context.user_id == "user123"

    # Correlation ID is preserved
    assert final_context.correlation_id == context.correlation_id


def test_request_context_elapsed_time():
    """Test elapsed time calculation."""
    context = RequestContext()

    # Small delay
    time.sleep(0.01)

    elapsed = context.elapsed_time
    assert elapsed > 0
    assert elapsed < 1  # Should be less than 1 second


def test_request_context_to_dict():
    """Test context serialization to dictionary."""
    context = (
        RequestContext()
        .with_endpoint("/shows/trending", "GET")
        .with_resource("show", "test-show")
        .with_parameters(limit=10)
        .with_user("user123")
    )

    context_dict = context.to_dict()

    # Check all fields are present
    assert "correlation_id" in context_dict
    assert context_dict["endpoint"] == "/shows/trending"
    assert context_dict["method"] == "GET"
    assert context_dict["resource_type"] == "show"
    assert context_dict["resource_id"] == "test-show"
    assert context_dict["parameters"] == {"limit": 10}
    assert context_dict["user_id"] == "user123"
    assert "elapsed_time" in context_dict


def test_context_variables():
    """Test context variable operations."""
    # Start with no context
    clear_current_context()
    assert get_current_context() is None

    # Set a context
    context = RequestContext()
    set_current_context(context)

    # Retrieve the same context
    retrieved = get_current_context()
    assert retrieved is not None
    assert retrieved is context
    assert retrieved.correlation_id == context.correlation_id

    # Clear context
    clear_current_context()
    assert get_current_context() is None


def test_create_new_context():
    """Test creating new context instances."""
    context1 = create_new_context()
    context2 = create_new_context()

    # Should be different instances with different correlation IDs
    assert context1 is not context2
    assert context1.correlation_id != context2.correlation_id


def test_get_correlation_id():
    """Test getting correlation ID from current context."""
    # No context set
    clear_current_context()
    assert get_correlation_id() is None

    # Set context
    context = RequestContext()
    set_current_context(context)

    # Get correlation ID
    correlation_id = get_correlation_id()
    assert correlation_id == context.correlation_id


def test_add_context_to_error_data_with_context():
    """Test adding context to error data when context exists."""
    # Set up context
    context = (
        RequestContext()
        .with_endpoint("/shows/trending", "GET")
        .with_resource("show", "test-show")
        .with_parameters(limit=10)
    )
    set_current_context(context)

    # Add context to error data
    error_data = {"error_type": "test_error", "message": "Test message"}
    enhanced_data = add_context_to_error_data(error_data)

    # Original data should be preserved
    assert enhanced_data["error_type"] == "test_error"
    assert enhanced_data["message"] == "Test message"

    # Context data should be added
    assert enhanced_data["correlation_id"] == context.correlation_id
    assert enhanced_data["endpoint"] == "/shows/trending"
    assert enhanced_data["method"] == "GET"
    assert enhanced_data["resource_type"] == "show"
    assert enhanced_data["resource_id"] == "test-show"
    assert enhanced_data["parameters"] == {"limit": 10}


def test_add_context_to_error_data_without_context():
    """Test adding context to error data when no context exists."""
    # Clear context
    clear_current_context()

    # Add context to error data
    error_data = {"error_type": "test_error", "message": "Test message"}
    enhanced_data = add_context_to_error_data(error_data)

    # Should return original data unchanged
    assert enhanced_data == error_data
    assert enhanced_data is not error_data  # Should be a copy


def test_correlation_id_format():
    """Test that correlation IDs are valid UUIDs."""
    context = RequestContext()

    # Should be a valid UUID string
    try:
        uuid.UUID(context.correlation_id)
    except ValueError:
        pytest.fail("Correlation ID is not a valid UUID")


def test_context_immutability():
    """Test that context modifications create new instances."""
    original = RequestContext()
    modified = original.with_endpoint("/test", "GET")

    # Should be different instances
    assert original is not modified

    # Original should be unchanged
    assert original.endpoint is None
    assert original.method is None

    # Modified should have new values
    assert modified.endpoint == "/test"
    assert modified.method == "GET"


def teardown_function():
    """Clean up after each test."""
    clear_current_context()
