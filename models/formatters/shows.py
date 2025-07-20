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

    @staticmethod
    def format_show_summary(show: dict[str, Any]) -> str:
        """Format basic show summary data.

        Args:
            show: Show data from Trakt API

        Returns:
            Formatted markdown text with basic show information
        """
        if not show:
            return "No show data available."

        title = show.get("title", "Unknown")
        year = show.get("year", "")
        year_str = f" ({year})" if year else ""
        overview = show.get("overview", "No overview available.")
        ids = show.get("ids", {})
        trakt_id = ids.get("trakt", "Unknown")

        result = f"## {title}{year_str}\n\n"
        result += f"{overview}\n\n"
        result += f"Trakt ID: {trakt_id}\n"

        return result

    @staticmethod
    def format_show_extended(show: dict[str, Any]) -> str:
        """Format extended show details data.

        Args:
            show: Extended show data from Trakt API

        Returns:
            Formatted markdown text with comprehensive show information
        """
        if not show:
            return "No show data available."

        # Basic info
        title = show.get("title", "Unknown")
        year = show.get("year", "")
        year_str = f" ({year})" if year else ""
        status = show.get("status", "unknown")
        tagline = show.get("tagline", "")
        overview = show.get("overview", "No overview available.")
        ids = show.get("ids", {})
        trakt_id = ids.get("trakt", "Unknown")

        # Format title with status
        result = f"## {title}{year_str} - {status.title().replace('_', ' ')}\n"

        # Add tagline if available
        if tagline:
            result += f"*{tagline}*\n"

        result += f"\n{overview}\n\n"

        # Production Details
        result += "### Production Details\n"
        result += f"- Status: {status.replace('_', ' ')}\n"

        if runtime := show.get("runtime"):
            result += f"- Runtime: {runtime} minutes\n"

        if certification := show.get("certification"):
            result += f"- Certification: {certification}\n"

        if network := show.get("network"):
            result += f"- Network: {network}\n"

        # Air time information
        if airs := show.get("airs"):
            day = airs.get("day", "")
            time = airs.get("time", "")
            timezone = airs.get("timezone", "")
            if day or time:
                air_time_str = "- Air Time: "
                if day and time:
                    air_time_str += f"{day}s at {time}"
                elif day:
                    air_time_str += f"{day}s"
                elif time:
                    air_time_str += f"at {time}"
                if timezone:
                    air_time_str += f" ({timezone})"
                result += air_time_str + "\n"

        if aired_episodes := show.get("aired_episodes"):
            result += f"- Aired Episodes: {aired_episodes}\n"

        if country := show.get("country"):
            result += f"- Country: {country.upper()}\n"

        if genres := show.get("genres"):
            genres_str = ", ".join(genres)
            result += f"- Genres: {genres_str}\n"

        if languages := show.get("languages"):
            languages_str = ", ".join(languages)
            result += f"- Languages: {languages_str}\n"

        if homepage := show.get("homepage"):
            result += f"- Homepage: {homepage}\n"

        # Ratings & Engagement
        result += "\n### Ratings & Engagement\n"

        rating = show.get("rating", 0)
        votes = show.get("votes", 0)
        result += f"- Rating: {rating:.1f}/10 ({votes} votes)\n"

        if comment_count := show.get("comment_count"):
            result += f"- Comments: {comment_count}\n"

        result += f"\nTrakt ID: {trakt_id}\n"

        return result
