"""Formatters for recommendation data."""

from typing import Protocol

from models.recommendations.recommendation import (
    FavoritedByEntry,
    TraktRecommendedMovie,
    TraktRecommendedShow,
)


class _RecommendationItem(Protocol):
    """Protocol for recommendation items with shared attributes."""

    title: str
    year: int | None
    ids: dict[str, str | int | None]
    favorited_by: list[FavoritedByEntry]


class RecommendationFormatters:
    """Helper class for formatting recommendation data for MCP responses."""

    @staticmethod
    def _format_recommendation_item(item: _RecommendationItem) -> str:
        """Format a single recommendation item.

        Args:
            item: A recommendation item (movie or show)

        Returns:
            Formatted markdown text for the item
        """
        year_str = f" ({item.year})" if item.year else ""
        trakt_id = item.ids.get("trakt", "")
        imdb_id = item.ids.get("imdb", "")

        result = f"### {item.title}{year_str}\n"
        if trakt_id:
            result += f"- **Trakt ID:** {trakt_id}\n"
        if imdb_id:
            result += f"- **IMDB:** {imdb_id}\n"
        if item.favorited_by:
            result += f"- **Favorited by:** {len(item.favorited_by)} user(s)\n"
        result += "\n"

        return result

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
            result += RecommendationFormatters._format_recommendation_item(movie)

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
            result += RecommendationFormatters._format_recommendation_item(show)

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
