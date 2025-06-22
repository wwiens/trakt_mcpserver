"""Configuration modules for the Trakt MCP server.

This module provides access to domain-focused configuration components:

- config.api: API-related constants (DEFAULT_LIMIT)
- config.auth: Authentication constants (AUTH_EXPIRATION, AUTH_POLL_INTERVAL, AUTH_VERIFICATION_URL)
- config.endpoints: Trakt API endpoints (TRAKT_ENDPOINTS)
- config.mcp: MCP server configuration (MCP_RESOURCES, TOOL_NAMES)

Use direct imports for better clarity:
    from config.api import DEFAULT_LIMIT
    from config.auth import AUTH_EXPIRATION
    from config.endpoints import TRAKT_ENDPOINTS
    from config.mcp.resources import MCP_RESOURCES
    from config.mcp.tools import TOOL_NAMES
"""
