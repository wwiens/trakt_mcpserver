# pyright: reportUnusedFunction=none
"""Authentication resources for the Trakt MCP server."""

from mcp.server.fastmcp import FastMCP

from client.auth import AuthClient
from config.mcp.resources import MCP_RESOURCES
from models.formatters.auth import AuthFormatters


async def get_auth_status() -> str:
    """Returns the current authentication status with Trakt.

    Returns:
        Formatted markdown text with authentication status
    """
    client = AuthClient()
    is_authenticated = client.is_authenticated()
    expires_at = client.get_token_expiry() if is_authenticated else None
    return AuthFormatters.format_auth_status(is_authenticated, expires_at)


def register_auth_resources(mcp: FastMCP) -> None:
    """Register authentication resources with the MCP server."""

    @mcp.resource(MCP_RESOURCES["user_auth_status"])
    async def auth_status_resource() -> str:
        return await get_auth_status()
