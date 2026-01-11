"""Authentication-specific MCP tool name definitions."""

from typing import Final

# Authentication MCP Tool Names
AUTH_TOOLS: Final[dict[str, str]] = {
    "start_device_auth": "start_device_auth",
    "check_auth_status": "check_auth_status",
    "clear_auth": "clear_auth",
}
