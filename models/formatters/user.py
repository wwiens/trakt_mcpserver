"""User formatting methods for the Trakt MCP server."""

from ..types import UserWatchedMovie, UserWatchedShow


class UserFormatters:
    """Helper class for formatting user-related data for MCP responses."""

    @staticmethod
    def format_user_watched_shows(shows: list[UserWatchedShow]) -> str:
        """Format user watched shows data for MCP resource."""
        result = "# Your Watched Shows on Trakt\n\n"

        if not shows:
            return (
                result
                + "You haven't watched any shows yet, "
                + "or you need to authenticate first."
            )

        for item in shows:
            show = item.get("show", {})
            last_watched = item.get("last_watched_at", "Unknown")
            plays = item.get("plays", 0)

            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""

            result += (
                f"- **{title}{year_str}** - Watched: {last_watched}, Plays: {plays}\n"
            )

            if overview := show.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_user_watched_movies(movies: list[UserWatchedMovie]) -> str:
        """Format user watched movies data for MCP resource."""
        result = "# Your Watched Movies on Trakt\n\n"

        if not movies:
            return (
                result
                + "You haven't watched any movies yet, "
                + "or you need to authenticate first."
            )

        for item in movies:
            movie = item.get("movie", {})
            last_watched = item.get("last_watched_at", "Unknown")
            plays = item.get("plays", 0)

            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""

            result += (
                f"- **{title}{year_str}** - Watched: {last_watched}, Plays: {plays}\n"
            )

            if overview := movie.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result
