"""Show formatting methods for the Trakt MCP server."""

from typing import Any


class ShowFormatters:
    """Helper class for formatting show-related data for MCP responses."""

    @staticmethod
    def format_trending_shows(shows: list[dict[str, Any]]) -> str:
        """Format trending shows data for MCP resource."""
        result = "# Trending Shows on Trakt\n\n"

        for item in shows:
            show = item.get("show", {})
            watchers = item.get("watchers", 0)

            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}** - {watchers} watchers\n"

            if overview := show.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_popular_shows(shows: list[dict[str, Any]]) -> str:
        """Format popular shows data for MCP resource."""
        result = "# Popular Shows on Trakt\n\n"

        for show in shows:
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}**\n"

            if overview := show.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_favorited_shows(shows: list[dict[str, Any]]) -> str:
        """Format favorited shows data for MCP resource."""
        result = "# Most Favorited Shows on Trakt\n\n"

        for item in shows:
            show = item.get("show", {})
            # The correct field is user_count in the API response
            user_count = item.get("user_count", 0)

            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}** - Favorited by {user_count} users\n"

            if overview := show.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_played_shows(shows: list[dict[str, Any]]) -> str:
        """Format played shows data for MCP resource."""
        result = "# Most Played Shows on Trakt\n\n"

        for item in shows:
            show = item.get("show", {})
            watcher_count = item.get("watcher_count", 0)
            play_count = item.get("play_count", 0)

            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}** - {watcher_count} watchers, {play_count} plays\n"

            if overview := show.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_watched_shows(shows: list[dict[str, Any]]) -> str:
        """Format watched shows data for MCP resource."""
        result = "# Most Watched Shows on Trakt\n\n"

        for item in shows:
            show = item.get("show", {})
            watcher_count = item.get("watcher_count", 0)

            title = show.get("title", "Unknown")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}** - Watched by {watcher_count} users\n"

            if overview := show.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_show_ratings(
        ratings: dict[str, Any], show_title: str = "Unknown show"
    ) -> str:
        """Format show ratings data for MCP resource.

        Args:
            ratings: The ratings data from Trakt API
            show_title: The title of the show

        Returns:
            Formatted markdown text with ratings information
        """
        result = f"# Ratings for {show_title}\n\n"

        if not ratings:
            return result + "No ratings data available."

        # Extract rating data
        average_rating = ratings.get("rating", 0)
        votes = ratings.get("votes", 0)
        distribution = ratings.get("distribution", {})

        # Format average rating with 2 decimal places
        result += f"**Average Rating:** {average_rating:.2f}/10 from {votes} votes\n\n"

        # Add distribution if available
        if distribution:
            result += "## Rating Distribution\n\n"
            result += "| Rating | Votes | Percentage |\n"
            result += "|--------|-------|------------|\n"

            # Calculate percentages for each rating
            for rating in range(10, 0, -1):  # 10 down to 1
                rating_str = str(rating)
                count = distribution.get(rating_str, 0)
                percentage = (count / votes * 100) if votes > 0 else 0

                result += f"| {rating}/10 | {count} | {percentage:.1f}% |\n"

        return result
