"""Formatters for recommendation data."""

from typing import Protocol

from models.recommendations.recommendation import (
    FavoritedByEntry,
    TraktRecommendedMovie,
    TraktRecommendedShow,
)
from models.types.ids import TraktIds


class _RecommendationItem(Protocol):
    """Protocol for recommendation items with shared attributes."""

    title: str
    year: int | None
    ids: TraktIds
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
        trakt_id = item.ids.trakt or ""
        imdb_id = item.ids.imdb or ""

        lines: list[str] = [f"### {item.title}{year_str}"]
        if trakt_id:
            lines.append(f"- **Trakt ID:** {trakt_id}")
        if imdb_id:
            lines.append(f"- **IMDB:** {imdb_id}")
        if item.favorited_by:
            lines.append(f"- **Favorited by:** {len(item.favorited_by)} user(s)")
        lines.append("")

        return "\n".join(lines)

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
        lines: list[str] = ["# Recommended Movies"]
        lines.append("")
        lines.append("_Personalized recommendations based on your viewing history_")
        lines.append("")

        if not movies:
            lines.append(
                "No recommendations available. Watch more content to improve recommendations!"
            )
            return "\n".join(lines)

        lines.extend(
            RecommendationFormatters._format_recommendation_item(movie)
            for movie in movies
        )

        return "\n".join(lines)

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
        lines: list[str] = ["# Recommended TV Shows"]
        lines.append("")
        lines.append("_Personalized recommendations based on your viewing history_")
        lines.append("")

        if not shows:
            lines.append(
                "No recommendations available. Watch more content to improve recommendations!"
            )
            return "\n".join(lines)

        lines.extend(
            RecommendationFormatters._format_recommendation_item(show) for show in shows
        )

        return "\n".join(lines)

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
