"""Authentication formatting methods for the Trakt MCP server."""


class AuthFormatters:
    """Helper class for formatting authentication-related data for MCP responses."""

    @staticmethod
    def format_auth_status(
        is_authenticated: bool, expires_at: int | None = None
    ) -> str:
        """Format authentication status for MCP resource."""
        if is_authenticated:
            return f"# Authentication Status\n\nYou are authenticated with Trakt.\nToken expires at: {expires_at}"
        else:
            return "# Authentication Status\n\nYou are not authenticated with Trakt.\nUse the `start_device_auth` tool to authenticate."

    @staticmethod
    def format_device_auth_instructions(
        user_code: str, verification_url: str, expires_in: int
    ) -> str:
        """Format device authentication instructions."""
        minutes = int(expires_in / 60)
        return f"""# Trakt Authentication Required

To access your personal Trakt data, you need to authenticate with Trakt.

1. Visit: **{verification_url}**
2. Enter code: **{user_code}**
3. Complete the authorization process on the Trakt website
4. **Important**: After authorizing on the Trakt website, please tell me "I've completed the authorization" so I can check your authentication status.

This code will expire in {minutes} minutes. I'll wait for your confirmation that you've completed the authorization step before checking.
"""
