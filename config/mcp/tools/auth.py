"""Authentication-specific MCP tool name definitions."""

from typing import Final

AUTH_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "start_device_auth",
        "check_auth_status",
        "clear_auth",
    }
)
