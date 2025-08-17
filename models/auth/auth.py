"""Authentication-related models for the Trakt MCP server."""

from pydantic import BaseModel, Field


class TraktDeviceCode(BaseModel):
    """Response from Trakt for device code authentication."""

    device_code: str
    user_code: str
    verification_url: str
    expires_in: int
    interval: int


class TraktAuthToken(BaseModel):
    """Authentication token response from Trakt."""

    access_token: str
    refresh_token: str
    expires_in: int
    created_at: int
    scope: str = "public"
    token_type: str = "bearer"  # noqa: S105 # OAuth token type, not a password


class DeviceTokenRequest(BaseModel):
    """Request model for device token exchange."""

    code: str = Field(min_length=1, description="Device code from Trakt")
