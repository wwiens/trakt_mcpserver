"""Formatters for recommendation data."""

from models.formatters.utils import format_pagination_header
from models.recommendations.recommendation import (
    TraktRecommendedMovie,
    TraktRecommendedShow,
)
from models.types.pagination import PaginatedResponse


class RecommendationFormatters:
    """Helper class for formatting recommendation data for MCP responses."""

    @staticmethod
    def format_movie_recommendations(
        data: list[TraktRecommendedMovie] | PaginatedResponse[TraktRecommendedMovie],
    ) -> str:
        """Format movie recommendations for MCP response.

        Args:
            data: Either a list of all movie recommendations or a paginated response

        Returns:
            Formatted markdown text with movie recommendations
        """
        result = "# Recommended Movies\n\n"
        result += "_Personalized recommendations based on your viewing history_\n\n"

        if isinstance(data, PaginatedResponse):
            result += format_pagination_header(data)
            movies = data.data
        else:
            movies = data

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
        data: list[TraktRecommendedShow] | PaginatedResponse[TraktRecommendedShow],
    ) -> str:
        """Format show recommendations for MCP response.

        Args:
            data: Either a list of all show recommendations or a paginated response

        Returns:
            Formatted markdown text with show recommendations
        """
        result = "# Recommended TV Shows\n\n"
        result += "_Personalized recommendations based on your viewing history_\n\n"

        if isinstance(data, PaginatedResponse):
            result += format_pagination_header(data)
            shows = data.data
        else:
            shows = data

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
