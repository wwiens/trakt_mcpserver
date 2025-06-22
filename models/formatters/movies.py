"""Movie formatting methods for the Trakt MCP server."""

from typing import Any


class MovieFormatters:
    """Helper class for formatting movie-related data for MCP responses."""

    @staticmethod
    def format_trending_movies(movies: list[dict[str, Any]]) -> str:
        """Format trending movies data for MCP resource."""
        result = "# Trending Movies on Trakt\n\n"

        for item in movies:
            movie = item.get("movie", {})
            watchers = item.get("watchers", 0)

            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}** - {watchers} watchers\n"

            if overview := movie.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_popular_movies(movies: list[dict[str, Any]]) -> str:
        """Format popular movies data for MCP resource."""
        result = "# Popular Movies on Trakt\n\n"

        for movie in movies:
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}**\n"

            if overview := movie.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_favorited_movies(movies: list[dict[str, Any]]) -> str:
        """Format favorited movies data for MCP resource."""
        result = "# Most Favorited Movies on Trakt\n\n"

        for item in movies:
            movie = item.get("movie", {})
            # The correct field is user_count in the API response
            user_count = item.get("user_count", 0)

            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}** - Favorited by {user_count} users\n"

            if overview := movie.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_played_movies(movies: list[dict[str, Any]]) -> str:
        """Format played movies data for MCP resource."""
        result = "# Most Played Movies on Trakt\n\n"

        for item in movies:
            movie = item.get("movie", {})
            watcher_count = item.get("watcher_count", 0)
            play_count = item.get("play_count", 0)

            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}** - {watcher_count} watchers, {play_count} plays\n"

            if overview := movie.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_watched_movies(movies: list[dict[str, Any]]) -> str:
        """Format watched movies data for MCP resource."""
        result = "# Most Watched Movies on Trakt\n\n"

        for item in movies:
            movie = item.get("movie", {})
            watcher_count = item.get("watcher_count", 0)

            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""

            result += f"- **{title}{year_str}** - Watched by {watcher_count} users\n"

            if overview := movie.get("overview"):
                result += f"  {overview}\n"

            result += "\n"

        return result

    @staticmethod
    def format_movie_ratings(
        ratings: dict[str, Any], movie_title: str = "Unknown movie"
    ) -> str:
        """Format movie ratings data for MCP resource.

        Args:
            ratings: The ratings data from Trakt API
            movie_title: The title of the movie

        Returns:
            Formatted markdown text with ratings information
        """
        result = f"# Ratings for {movie_title}\n\n"

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
