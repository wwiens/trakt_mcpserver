"""Formatters for recommendation data."""

from models.recommendations.recommendation import (
    TraktRecommendedMovie,
    TraktRecommendedShow,
)


class RecommendationFormatters:
    """Helper class for formatting recommendation data for MCP responses."""

    @staticmethod
    def format_movie_recommendations(
        movies: list[TraktRecommendedMovie],
    ) -> str:
        """Format movie recommendations for MCP response.

        Args:
            movies: List of movie recommendations

        Returns:
            Formatted markdown text with movie recommendations
        """
        result = "# Recommended Movies\n\n"
        result += "_Personalized recommendations based on your viewing history_\n\n"

        if not movies:
            return f"{result}No recommendations available. Watch more content to improve recommendations!\n"

        for movie in movies:
            title = movie.title
            year = movie.year
            year_str = f" ({year})" if year else ""

            ids = movie.ids
            trakt_id = ids.get("trakt", "")
            imdb_id = ids.get("imdb", "")

            result += f"### {title}{year_str}\n"
            if trakt_id:
                result += f"- **Trakt ID:** {trakt_id}\n"
            if imdb_id:
                result += f"- **IMDB:** {imdb_id}\n"

            if movie.favorited_by:
                fav_count = len(movie.favorited_by)
                result += f"- **Favorited by:** {fav_count} user(s)\n"

            result += "\n"

        return result

    @staticmethod
    def format_show_recommendations(
        shows: list[TraktRecommendedShow],
    ) -> str:
        """Format show recommendations for MCP response.

        Args:
            shows: List of show recommendations

        Returns:
            Formatted markdown text with show recommendations
        """
        result = "# Recommended TV Shows\n\n"
        result += "_Personalized recommendations based on your viewing history_\n\n"

        if not shows:
            return f"{result}No recommendations available. Watch more content to improve recommendations!\n"

        for show in shows:
            title = show.title
            year = show.year
            year_str = f" ({year})" if year else ""

            ids = show.ids
            trakt_id = ids.get("trakt", "")
            imdb_id = ids.get("imdb", "")

            result += f"### {title}{year_str}\n"
            if trakt_id:
                result += f"- **Trakt ID:** {trakt_id}\n"
            if imdb_id:
                result += f"- **IMDB:** {imdb_id}\n"

            if show.favorited_by:
                fav_count = len(show.favorited_by)
                result += f"- **Favorited by:** {fav_count} user(s)\n"

            result += "\n"

        return result

    @staticmethod
    def format_hide_result(item_type: str, item_id: str) -> str:
        """Format hide recommendation result.

        Args:
            item_type: Type of item hidden ("movie" or "show")
            item_id: The ID used to hide the item

        Returns:
            Formatted success message
        """
        return (
            f"Successfully hidden {item_type} `{item_id}` from future recommendations."
        )

    @staticmethod
    def format_unhide_result(item_type: str, item_id: str) -> str:
        """Format unhide recommendation result.

        Args:
            item_type: Type of item unhidden ("movie" or "show")
            item_id: The ID used to unhide the item

        Returns:
            Formatted success message
        """
        return (
            f"Successfully unhidden {item_type} `{item_id}` for future recommendations."
        )
