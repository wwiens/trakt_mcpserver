"""Movie formatting methods for the Trakt MCP server."""

from models.types import (
    FavoritedMovieWrapper,
    MovieResponse,
    PlayedMovieWrapper,
    TraktRating,
    TrendingWrapper,
    WatchedMovieWrapper,
)
from models.types.pagination import PaginatedResponse


class MovieFormatters:
    """Helper class for formatting movie-related data for MCP responses."""

    @staticmethod
    def format_trending_movies(
        data: list[TrendingWrapper] | PaginatedResponse[TrendingWrapper],
    ) -> str:
        """Format trending movies data for MCP resource.

        Args:
            data: Either a list of all trending movies or a paginated response

        Returns:
            Formatted markdown text with trending movies
        """
        result = "# Trending Movies on Trakt\n\n"

        # Handle pagination metadata if present
        if isinstance(data, PaginatedResponse):
            result += f"📄 **{data.page_info_summary()}**\n\n"

            # Add navigation hints
            navigation_hints: list[str] = []
            if data.pagination.has_previous_page:
                navigation_hints.append(
                    f"Previous: page {data.pagination.previous_page}"
                )
            if data.pagination.has_next_page:
                navigation_hints.append(f"Next: page {data.pagination.next_page}")

            if navigation_hints:
                result += f"📍 **Navigation:** {' | '.join(navigation_hints)}\n\n"

            movies = data.data
        else:
            movies = data

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
    def format_popular_movies(
        data: list[MovieResponse] | PaginatedResponse[MovieResponse],
    ) -> str:
        """Format popular movies data for MCP resource.

        Args:
            data: Either a list of all popular movies or a paginated response

        Returns:
            Formatted markdown text with popular movies
        """
        result = "# Popular Movies on Trakt\n\n"

        # Handle pagination metadata if present
        if isinstance(data, PaginatedResponse):
            result += f"📄 **{data.page_info_summary()}**\n\n"

            # Add navigation hints
            navigation_hints: list[str] = []
            if data.pagination.has_previous_page:
                navigation_hints.append(
                    f"Previous: page {data.pagination.previous_page}"
                )
            if data.pagination.has_next_page:
                navigation_hints.append(f"Next: page {data.pagination.next_page}")

            if navigation_hints:
                result += f"📍 **Navigation:** {' | '.join(navigation_hints)}\n\n"

            movies = data.data
        else:
            movies = data

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
    def format_favorited_movies(
        data: list[FavoritedMovieWrapper] | PaginatedResponse[FavoritedMovieWrapper],
    ) -> str:
        """Format favorited movies data for MCP resource.

        Args:
            data: Either a list of all favorited movies or a paginated response

        Returns:
            Formatted markdown text with favorited movies
        """
        result = "# Most Favorited Movies on Trakt\n\n"

        # Handle pagination metadata if present
        if isinstance(data, PaginatedResponse):
            result += f"📄 **{data.page_info_summary()}**\n\n"

            # Add navigation hints
            navigation_hints: list[str] = []
            if data.pagination.has_previous_page:
                navigation_hints.append(
                    f"Previous: page {data.pagination.previous_page}"
                )
            if data.pagination.has_next_page:
                navigation_hints.append(f"Next: page {data.pagination.next_page}")

            if navigation_hints:
                result += f"📍 **Navigation:** {' | '.join(navigation_hints)}\n\n"

            movies = data.data
        else:
            movies = data

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
    def format_played_movies(
        data: list[PlayedMovieWrapper] | PaginatedResponse[PlayedMovieWrapper],
    ) -> str:
        """Format played movies data for MCP resource.

        Args:
            data: Either a list of all played movies or a paginated response

        Returns:
            Formatted markdown text with played movies
        """
        result = "# Most Played Movies on Trakt\n\n"

        # Handle pagination metadata if present
        if isinstance(data, PaginatedResponse):
            result += f"📄 **{data.page_info_summary()}**\n\n"

            # Add navigation hints
            navigation_hints: list[str] = []
            if data.pagination.has_previous_page:
                navigation_hints.append(
                    f"Previous: page {data.pagination.previous_page}"
                )
            if data.pagination.has_next_page:
                navigation_hints.append(f"Next: page {data.pagination.next_page}")

            if navigation_hints:
                result += f"📍 **Navigation:** {' | '.join(navigation_hints)}\n\n"

            movies = data.data
        else:
            movies = data

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
    def format_watched_movies(
        data: list[WatchedMovieWrapper] | PaginatedResponse[WatchedMovieWrapper],
    ) -> str:
        """Format watched movies data for MCP resource.

        Args:
            data: Either a list of all watched movies or a paginated response

        Returns:
            Formatted markdown text with watched movies
        """
        result = "# Most Watched Movies on Trakt\n\n"

        # Handle pagination metadata if present
        if isinstance(data, PaginatedResponse):
            result += f"📄 **{data.page_info_summary()}**\n\n"

            # Add navigation hints
            navigation_hints: list[str] = []
            if data.pagination.has_previous_page:
                navigation_hints.append(
                    f"Previous: page {data.pagination.previous_page}"
                )
            if data.pagination.has_next_page:
                navigation_hints.append(f"Next: page {data.pagination.next_page}")

            if navigation_hints:
                result += f"📍 **Navigation:** {' | '.join(navigation_hints)}\n\n"

            movies = data.data
        else:
            movies = data

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
        ratings: TraktRating, movie_title: str = "Unknown movie"
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

    @staticmethod
    def format_movie_summary(movie: MovieResponse) -> str:
        """Format basic movie summary data.

        Args:
            movie: Movie data from Trakt API

        Returns:
            Formatted markdown text with basic movie information (title, year, ID only)
        """
        if not movie:
            return "No movie data available."

        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        year_str = f" ({year})" if year else ""
        ids = movie.get("ids", {})
        trakt_id = ids.get("trakt", "Unknown")

        result = f"## {title}{year_str}\n\n"
        result += f"Trakt ID: {trakt_id}\n"

        return result

    @staticmethod
    def format_movie_extended(movie: MovieResponse) -> str:
        """Format extended movie details data.

        Args:
            movie: Extended movie data from Trakt API

        Returns:
            Formatted markdown text with comprehensive movie information
        """
        if not movie:
            return "No movie data available."

        # Basic info
        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        year_str = f" ({year})" if year else ""
        status = movie.get("status", "unknown")
        tagline = movie.get("tagline", "")
        overview = movie.get("overview", "No overview available.")
        ids = movie.get("ids", {})
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

        if runtime := movie.get("runtime"):
            result += f"- Runtime: {runtime} minutes\n"

        if certification := movie.get("certification"):
            result += f"- Certification: {certification}\n"

        if released := movie.get("released"):
            result += f"- Released: {released}\n"

        if country := movie.get("country"):
            result += f"- Country: {country.upper()}\n"

        if genres := movie.get("genres"):
            genres_str = ", ".join(genres)
            result += f"- Genres: {genres_str}\n"

        if languages := movie.get("languages"):
            languages_str = ", ".join(languages)
            result += f"- Languages: {languages_str}\n"

        if homepage := movie.get("homepage"):
            result += f"- Homepage: {homepage}\n"

        # Ratings & Engagement
        result += "\n### Ratings & Engagement\n"

        rating = movie.get("rating", 0)
        votes = movie.get("votes", 0)
        result += f"- Rating: {rating:.1f}/10 ({votes} votes)\n"

        if comment_count := movie.get("comment_count"):
            result += f"- Comments: {comment_count}\n"

        result += f"\nTrakt ID: {trakt_id}\n"

        return result
