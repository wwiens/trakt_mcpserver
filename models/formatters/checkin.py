"""Check-in formatting methods for the Trakt MCP server."""

from typing import Any


class CheckinFormatters:
    """Helper class for formatting check-in related data for MCP responses."""

    @staticmethod
    def format_checkin_response(response: dict[str, Any]) -> str:
        """Format the checkin response from Trakt API.

        Args:
            response: The checkin response data

        Returns:
            Formatted response message
        """
        try:
            # Extract show and episode info
            show = response.get("show", {})
            episode = response.get("episode", {})

            show_title = show.get("title", "Unknown show")
            episode_title = episode.get("title", "Unknown episode")
            season = episode.get("season", 0)
            number = episode.get("number", 0)

            # Format the success message
            message = "# Successfully Checked In\n\n"
            message += f"You are now checked in to **{show_title}** - S{season:02d}E{number:02d}: {episode_title}\n\n"

            # Add watched_at time if available
            if watched_at := response.get("watched_at"):
                # Try to format the timestamp for better readability
                try:
                    # Format the timestamp (removing the 'Z' and truncating milliseconds)
                    watched_time = (
                        watched_at.replace("Z", "").split(".")[0].replace("T", " ")
                    )
                    message += f"Watched at: {watched_time} UTC\n\n"
                except Exception:
                    message += f"Watched at: {watched_at}\n\n"

            # Add sharing info if available
            if sharing := response.get("sharing", {}):
                platforms: list[str] = []
                for platform, shared in sharing.items():
                    if shared:
                        platforms.append(platform.capitalize())

                if platforms:
                    message += f"Shared on: {', '.join(platforms)}\n\n"

            # Add checkin ID if available
            if checkin_id := response.get("id"):
                message += f"Checkin ID: {checkin_id}\n"

            return message

        except Exception:
            # Fallback for any parsing errors
            return f"Successfully checked in to the show.\n\nDetails: {response!s}"
