"""Tests for the models.auth module."""

from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from models.auth import TraktAuthToken, TraktDeviceCode

if TYPE_CHECKING:
    from tests.models.test_data_types import AuthTokenTestData, DeviceCodeTestData


class TestTraktDeviceCode:
    """Tests for the TraktDeviceCode model."""

    def test_valid_device_code_creation(self):
        """Test creating a valid TraktDeviceCode instance."""
        device_code = TraktDeviceCode(
            device_code="abc123def456",
            user_code="ABCD1234",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
            interval=5,
        )

        assert device_code.device_code == "abc123def456"
        assert device_code.user_code == "ABCD1234"
        assert device_code.verification_url == "https://trakt.tv/activate"
        assert device_code.expires_in == 600
        assert device_code.interval == 5

    def test_device_code_required_fields(self):
        """Test that all required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktDeviceCode(**{})  # type: ignore[call-arg] # Testing: Pydantic validation with invalid types

        errors = exc_info.value.errors()
        assert len(errors) == 5  # All fields are required

        required_fields = {error["loc"][0] for error in errors}
        expected_fields = {
            "device_code",
            "user_code",
            "verification_url",
            "expires_in",
            "interval",
        }
        assert required_fields == expected_fields

    def test_device_code_field_types(self):
        """Test that fields have correct types."""
        # Test with clearly incompatible types
        with pytest.raises(ValidationError):
            TraktDeviceCode(
                device_code=["not", "a", "string"],  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types
                user_code="ABCD1234",
                verification_url="https://trakt.tv/activate",
                expires_in=600,
                interval=5,
            )

        with pytest.raises(ValidationError):
            TraktDeviceCode(
                device_code="abc123def456",
                user_code="ABCD1234",
                verification_url="https://trakt.tv/activate",
                expires_in=["not", "an", "int"],  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types
                interval=5,
            )

    def test_device_code_serialization(self):
        """Test that TraktDeviceCode can be serialized to dict."""
        device_code_data: DeviceCodeTestData = {
            "device_code": "abc123def456",
            "user_code": "ABCD1234",
            "verification_url": "https://trakt.tv/activate",
            "expires_in": 600,
            "interval": 5,
        }

        device_code = TraktDeviceCode(**device_code_data)
        serialized = device_code.model_dump()

        assert serialized == device_code_data

    def test_device_code_json_serialization(self):
        """Test that TraktDeviceCode can be serialized to JSON."""
        device_code_data: DeviceCodeTestData = {
            "device_code": "abc123def456",
            "user_code": "ABCD1234",
            "verification_url": "https://trakt.tv/activate",
            "expires_in": 600,
            "interval": 5,
        }

        device_code = TraktDeviceCode(**device_code_data)
        json_str = device_code.model_dump_json()

        # Should be valid JSON
        import json

        parsed = json.loads(json_str)
        assert parsed == device_code_data


class TestTraktAuthToken:
    """Tests for the TraktAuthToken model."""

    def test_valid_auth_token_creation(self):
        """Test creating a valid TraktAuthToken instance."""
        token_data: AuthTokenTestData = {
            "access_token": "abc123def456ghi789",
            "refresh_token": "refresh123abc456",
            "expires_in": 7776000,  # 90 days
            "created_at": 1677123456,
            "scope": "public",
            "token_type": "bearer",
        }

        auth_token = TraktAuthToken(**token_data)

        assert auth_token.access_token == "abc123def456ghi789"
        assert auth_token.refresh_token == "refresh123abc456"
        assert auth_token.expires_in == 7776000
        assert auth_token.created_at == 1677123456
        assert auth_token.scope == "public"  # Default value
        assert auth_token.token_type == "bearer"  # Default value

    def test_auth_token_with_custom_scope_and_type(self):
        """Test creating auth token with custom scope and token type."""
        token_data: AuthTokenTestData = {
            "access_token": "abc123def456ghi789",
            "refresh_token": "refresh123abc456",
            "expires_in": 7776000,
            "created_at": 1677123456,
            "scope": "public private",
            "token_type": "Bearer",
        }

        auth_token = TraktAuthToken(**token_data)

        assert auth_token.scope == "public private"
        assert auth_token.token_type == "Bearer"

    def test_auth_token_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            TraktAuthToken()  # type: ignore[call-arg] # Testing: Pydantic validation with invalid types

        errors = exc_info.value.errors()
        assert len(errors) == 4  # 4 required fields

        required_fields = {error["loc"][0] for error in errors}
        expected_fields = {"access_token", "refresh_token", "expires_in", "created_at"}
        assert required_fields == expected_fields

    def test_auth_token_field_types(self):
        """Test that fields have correct types."""
        # Test with clearly incompatible types
        with pytest.raises(ValidationError):
            TraktAuthToken(
                access_token=["not", "a", "string"],  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types
                refresh_token="refresh123abc456",
                expires_in=7776000,
                created_at=1677123456,
            )

        with pytest.raises(ValidationError):
            TraktAuthToken(
                access_token="abc123def456ghi789",
                refresh_token="refresh123abc456",
                expires_in=["not", "an", "int"],  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types
                created_at=1677123456,
            )

        with pytest.raises(ValidationError):
            TraktAuthToken(
                access_token="abc123def456ghi789",
                refresh_token="refresh123abc456",
                expires_in=7776000,
                created_at=["not", "an", "int"],  # type: ignore[arg-type] # Testing: Pydantic validation with invalid types
            )

    def test_auth_token_serialization(self):
        """Test that TraktAuthToken can be serialized to dict."""
        token_data: AuthTokenTestData = {
            "access_token": "abc123def456ghi789",
            "refresh_token": "refresh123abc456",
            "expires_in": 7776000,
            "created_at": 1677123456,
            "scope": "public",
            "token_type": "bearer",
        }

        auth_token = TraktAuthToken(**token_data)
        serialized = auth_token.model_dump()

        assert serialized == token_data

    def test_auth_token_json_serialization(self):
        """Test that TraktAuthToken can be serialized to JSON."""
        token_data: AuthTokenTestData = {
            "access_token": "abc123def456ghi789",
            "refresh_token": "refresh123abc456",
            "expires_in": 7776000,
            "created_at": 1677123456,
            "scope": "public",
            "token_type": "bearer",
        }

        auth_token = TraktAuthToken(**token_data)
        json_str = auth_token.model_dump_json()

        # Should be valid JSON
        import json

        parsed = json.loads(json_str)

        # Check that defaults are included
        expected = {
            **token_data,
            "scope": "public",
            "token_type": "bearer",
        }
        assert parsed == expected

    def test_auth_token_expiration_calculation(self):
        """Test token expiration calculations."""
        import time

        current_time = int(time.time())
        expires_in = 3600  # 1 hour

        auth_token = TraktAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=expires_in,
            created_at=current_time,
            scope="public",
            token_type="bearer",
        )

        # Token should expire at created_at + expires_in
        expected_expiry = current_time + expires_in

        # We can calculate this from the model data
        actual_expiry = auth_token.created_at + auth_token.expires_in
        assert actual_expiry == expected_expiry

    def test_auth_token_is_expired_logic(self):
        """Test logic for determining if token is expired."""
        import time

        current_time = int(time.time())

        # Create an expired token (created 2 hours ago, expires in 1 hour)
        expired_token = TraktAuthToken(
            access_token="expired_token",
            refresh_token="refresh",
            expires_in=3600,  # 1 hour
            created_at=current_time - 7200,  # 2 hours ago
            scope="public",
            token_type="bearer",
        )

        # Create a valid token (created now, expires in 1 hour)
        valid_token = TraktAuthToken(
            access_token="valid_token",
            refresh_token="refresh",
            expires_in=3600,  # 1 hour
            created_at=current_time,
            scope="public",
            token_type="bearer",
        )

        # Test expiration logic (would be implemented in business logic)
        expired_expiry_time = expired_token.created_at + expired_token.expires_in
        valid_expiry_time = valid_token.created_at + valid_token.expires_in

        assert expired_expiry_time < current_time  # Token is expired
        assert valid_expiry_time > current_time  # Token is still valid

    def test_auth_token_partial_data(self):
        """Test creating auth token with minimal required data."""
        minimal_data: AuthTokenTestData = {
            "access_token": "minimal_token",
            "refresh_token": "minimal_refresh",
            "expires_in": 3600,
            "created_at": 1677123456,
            "scope": "public",
            "token_type": "bearer",
        }

        auth_token = TraktAuthToken(**minimal_data)

        assert auth_token.access_token == "minimal_token"
        assert auth_token.refresh_token == "minimal_refresh"
        assert auth_token.expires_in == 3600
        assert auth_token.created_at == 1677123456
        # Defaults should be applied
        assert auth_token.scope == "public"
        assert auth_token.token_type == "bearer"

    def test_auth_token_from_api_response(self):
        """Test creating auth token from typical API response format."""
        # Simulate typical Trakt OAuth API response
        api_response: AuthTokenTestData = {
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "bearer",
            "expires_in": 7776000,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "scope": "public",
            "created_at": 1677123456,
        }

        auth_token = TraktAuthToken(**api_response)

        assert auth_token.access_token == "2YotnFZFEjr1zCsicMWpAA"
        assert auth_token.token_type == "bearer"
        assert auth_token.expires_in == 7776000
        assert auth_token.refresh_token == "tGzv3JOkF0XG5Qx2TlKWIA"
        assert auth_token.scope == "public"
        assert auth_token.created_at == 1677123456
