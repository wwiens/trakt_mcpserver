# pyright: reportUnusedFunction=none
"""Authentication tools for the Trakt MCP server."""

import logging
import time
from typing import Any

from mcp.server.fastmcp import FastMCP

from client.auth import AuthClient
from config.auth import AUTH_VERIFICATION_URL
from config.mcp.tools import TOOL_NAMES
from models.formatters.auth import AuthFormatters

# Set up logging
logger = logging.getLogger("trakt_mcp")

# Authentication storage for active device code flows
active_auth_flow: dict[str, Any] = {}


async def start_device_auth() -> str:
    """Start the device authentication flow with Trakt.

    Returns:
        Authentication instructions for the user
    """
    client = AuthClient()

    # Check if already authenticated
    if client.is_authenticated():
        return "You are already authenticated with Trakt."

    # Get device code
    device_code_response = await client.get_device_code()

    # Store active auth flow
    global active_auth_flow
    active_auth_flow = {
        "device_code": device_code_response.device_code,
        "expires_at": int(time.time()) + device_code_response.expires_in,
        "interval": device_code_response.interval,
        "last_poll": 0,
    }

    logger.info(f"Started device auth flow: {active_auth_flow}")

    # Return instructions for the user
    instructions = AuthFormatters.format_device_auth_instructions(
        device_code_response.user_code,
        AUTH_VERIFICATION_URL,
        device_code_response.expires_in,
    )

    return f"""{instructions}

I won't automatically check your authentication status until you tell me you've completed the authorization. Once you've finished the authorization process on the Trakt website, simply tell me "I've completed the authorization" and I'll verify it for you."""


async def check_auth_status() -> str:
    """Check the status of an ongoing device authentication flow.

    Returns:
        Status of the authentication process
    """
    client = AuthClient()

    # Check if already authenticated
    if client.is_authenticated():
        return """# Authentication Successful!

You are now authenticated with Trakt. You can access your personal data using tools like `fetch_user_watched_shows` and `fetch_user_watched_movies`.

If you want to log out at any point, you can use the `clear_auth` tool."""

    # Check if there's an active flow
    global active_auth_flow
    if not active_auth_flow or "device_code" not in active_auth_flow:
        return "No active authentication flow. Use the `start_device_auth` tool to begin authentication."

    # Check if flow is expired
    current_time = int(time.time())
    if current_time > active_auth_flow["expires_at"]:
        active_auth_flow = {}
        return "Authentication flow expired. Please start a new one with the `start_device_auth` tool."

    # Check if it's too early to poll again
    if current_time - active_auth_flow["last_poll"] < active_auth_flow["interval"]:
        seconds_to_wait = active_auth_flow["interval"] - (
            current_time - active_auth_flow["last_poll"]
        )
        return f"Please wait {seconds_to_wait} seconds before checking again."

    # Update last poll time
    active_auth_flow["last_poll"] = current_time

    # Try to get token
    token = await client.get_device_token(active_auth_flow["device_code"])
    if token:
        # Authentication successful
        active_auth_flow = {}
        return """# Authentication Successful!

You have successfully authorized the Trakt MCP application. You can now access your personal Trakt data using tools like `fetch_user_watched_shows` and `fetch_user_watched_movies`.

If you want to log out at any point, you can use the `clear_auth` tool."""
    else:
        # Still waiting for user to authorize
        return """# Authorization Pending

I don't see that you've completed the authorization yet. Please make sure to:

1. Visit the Trakt activation page
2. Enter your code
3. Approve the authorization request

If you've already done this and are still seeing this message, please wait a few seconds and try again by telling me "Please check my authorization status"."""


async def clear_auth() -> str:
    """Clear the authentication token, effectively logging the user out of Trakt.

    Returns:
        Status message about the logout
    """
    client = AuthClient()

    # Clear any active authentication flow
    global active_auth_flow
    active_auth_flow = {}

    # Try to clear the token
    if client.clear_auth_token():
        return "You have been successfully logged out of Trakt. Your authentication token has been cleared."
    else:
        return "You were not authenticated with Trakt."


def register_auth_tools(mcp: FastMCP) -> None:
    """Register authentication tools with the MCP server."""

    @mcp.tool(
        name=TOOL_NAMES["start_device_auth"],
        description="Start the device authentication flow with Trakt TV",
    )
    async def start_device_auth_tool() -> str:
        return await start_device_auth()

    @mcp.tool(
        name=TOOL_NAMES["check_auth_status"],
        description="Check the status of an ongoing device authentication flow",
    )
    async def check_auth_status_tool() -> str:
        return await check_auth_status()

    @mcp.tool(
        name=TOOL_NAMES["clear_auth"],
        description="Clear the authentication token and log out of Trakt",
    )
    async def clear_auth_tool() -> str:
        return await clear_auth()
