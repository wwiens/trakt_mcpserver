"""Movie formatting methods for the Trakt MCP server."""

from models.formatters.utils import (
    MAX_OVERVIEW_LENGTH,
    format_media_list,
    format_pagination_header,
    format_rating_distribution,
    format_title_year,
)
from models.types import (
    AnticipatedMovieWrapper,
    BoxOfficeMovieWrapper,
    CastMember,
    CrewMember,
    FavoritedMovieWrapper,
    MovieResponse,
    PeopleResponse,
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
        """Format trending movies data for MCP resource."""
        return format_media_list(
            data,
            heading="Trending Movies on Trakt",
            media_key="movie",
            format_metric=lambda item: f"{item.get('watchers', 0)} watchers",
        )

    @staticmethod
    def format_popular_movies(
        data: list[MovieResponse] | PaginatedResponse[MovieResponse],
    ) -> str:
        """Format popular movies data for MCP resource."""
        return format_media_list(
            data,
            heading="Popular Movies on Trakt",
            media_key=None,
        )

    @staticmethod
    def format_favorited_movies(
        data: list[FavoritedMovieWrapper] | PaginatedResponse[FavoritedMovieWrapper],
    ) -> str:
        """Format favorited movies data for MCP resource."""
        return format_media_list(
            data,
            heading="Most Favorited Movies on Trakt",
            media_key="movie",
            format_metric=lambda item: (
                f"Favorited by {item.get('user_count', 0)} users"
            ),
        )

    @staticmethod
    def format_played_movies(
        data: list[PlayedMovieWrapper] | PaginatedResponse[PlayedMovieWrapper],
    ) -> str:
        """Format played movies data for MCP resource."""
        return format_media_list(
            data,
            heading="Most Played Movies on Trakt",
            media_key="movie",
            format_metric=lambda item: (
                f"{item.get('watcher_count', 0)} watchers, "
                f"{item.get('play_count', 0)} plays"
            ),
        )

    @staticmethod
    def format_watched_movies(
        data: list[WatchedMovieWrapper] | PaginatedResponse[WatchedMovieWrapper],
    ) -> str:
        """Format watched movies data for MCP resource."""
        return format_media_list(
            data,
            heading="Most Watched Movies on Trakt",
            media_key="movie",
            format_metric=lambda item: (
                f"Watched by {item.get('watcher_count', 0)} users"
            ),
        )

    @staticmethod
    def format_anticipated_movies(
        data: list[AnticipatedMovieWrapper]
        | PaginatedResponse[AnticipatedMovieWrapper],
    ) -> str:
        """Format anticipated movies data for MCP resource."""
        return format_media_list(
            data,
            heading="Most Anticipated Movies on Trakt",
            media_key="movie",
            format_metric=lambda item: f"On {item.get('list_count', 0)} lists",
        )

    @staticmethod
    def format_boxoffice_movies(data: list[BoxOfficeMovieWrapper]) -> str:
        """Format box office movies data for MCP resource."""
        lines: list[str] = ["# Box Office Movies (U.S. Weekend)\n"]

        if not data:
            return (
                "# Box Office Movies (U.S. Weekend)\n\nNo box office data available.\n"
            )

        for i, item in enumerate(data, 1):
            movie = item.get("movie", {})
            revenue = item.get("revenue", 0)

            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            title_str = format_title_year(title, year)

            lines.append(f"- **#{i} {title_str}** - ${revenue:,} revenue")

            if overview := movie.get("overview"):
                if len(overview) > MAX_OVERVIEW_LENGTH:
                    overview = overview[: MAX_OVERVIEW_LENGTH - 3] + "..."
                lines.append(f"  {overview}")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_movie_ratings(
        ratings: TraktRating, movie_title: str = "Unknown movie"
    ) -> str:
        """Format movie ratings data for MCP resource."""
        lines: list[str] = [f"# Ratings for {movie_title}\n"]

        if not ratings:
            return f"# Ratings for {movie_title}\n\nNo ratings data available."

        average_rating = ratings.get("rating", 0)
        votes = ratings.get("votes", 0)
        distribution = ratings.get("distribution", {})

        lines.append(
            f"**Average Rating:** {average_rating:.2f}/10 from {votes} votes\n"
        )

        if distribution:
            lines.append(format_rating_distribution(distribution, votes))

        return "\n".join(lines)

    @staticmethod
    def format_movie_summary(movie: MovieResponse) -> str:
        """Format basic movie summary data."""
        if not movie:
            return "No movie data available."

        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        title_str = format_title_year(title, year)
        ids = movie.get("ids", {})
        trakt_id = ids.get("trakt", "Unknown")

        lines: list[str] = [f"## {title_str}\n"]
        lines.append(f"Trakt ID: {trakt_id}")

        return "\n".join(lines)

    @staticmethod
    def format_movie_extended(movie: MovieResponse) -> str:
        """Format extended movie details data."""
        if not movie:
            return "No movie data available."

        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        title_str = format_title_year(title, year)
        status = movie.get("status", "unknown")
        tagline = movie.get("tagline", "")
        overview = movie.get("overview", "No overview available.")
        ids = movie.get("ids", {})
        trakt_id = ids.get("trakt", "Unknown")

        lines: list[str] = [f"## {title_str} - {status.title().replace('_', ' ')}"]

        if tagline:
            lines.append(f"*{tagline}*")

        lines.append(f"\n{overview}\n")
        lines.append("### Production Details")
        lines.append(f"- Status: {status.replace('_', ' ')}")

        if runtime := movie.get("runtime"):
            lines.append(f"- Runtime: {runtime} minutes")

        if certification := movie.get("certification"):
            lines.append(f"- Certification: {certification}")

        if released := movie.get("released"):
            lines.append(f"- Released: {released}")

        if country := movie.get("country"):
            lines.append(f"- Country: {country.upper()}")

        if genres := movie.get("genres"):
            genres_str = ", ".join(genres)
            lines.append(f"- Genres: {genres_str}")

        if languages := movie.get("languages"):
            languages_str = ", ".join(languages)
            lines.append(f"- Languages: {languages_str}")

        if homepage := movie.get("homepage"):
            lines.append(f"- Homepage: {homepage}")

        lines.append("\n### Ratings & Engagement")

        rating = movie.get("rating", 0)
        votes = movie.get("votes", 0)
        lines.append(f"- Rating: {rating:.1f}/10 ({votes} votes)")

        if comment_count := movie.get("comment_count"):
            lines.append(f"- Comments: {comment_count}")

        lines.append(f"\nTrakt ID: {trakt_id}")

        return "\n".join(lines)

    @staticmethod
    def format_related_movies(
        data: list[MovieResponse] | PaginatedResponse[MovieResponse],
    ) -> str:
        """Format related movies data for MCP resource."""
        lines: list[str] = ["# Related Movies\n"]

        if isinstance(data, PaginatedResponse):
            lines.append(format_pagination_header(data))
            movies = data.data
        else:
            movies = data

        if not movies:
            return "# Related Movies\n\nNo related movies found.\n"

        for movie in movies:
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            title_str = format_title_year(title, year)

            lines.append(f"- **{title_str}**")

            if overview := movie.get("overview"):
                if len(overview) > MAX_OVERVIEW_LENGTH:
                    overview = overview[: MAX_OVERVIEW_LENGTH - 3] + "..."
                lines.append(f"  {overview}")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_movie_people(people: PeopleResponse, movie_title: str) -> str:
        """Format movie cast and crew data."""
        if not people:
            return f"# People for {movie_title}\n\nNo people data available."

        cast: list[CastMember] = people.get("cast", [])
        crew: dict[str, list[CrewMember]] = people.get("crew", {})

        if not cast and not crew:
            return f"# People for {movie_title}\n\nNo people data available."

        lines: list[str] = [f"# People for {movie_title}\n"]

        if cast:
            lines.append("## Cast\n")
            for member in cast:
                person = member.get("person", {})
                name = person.get("name", "Unknown")
                characters = member.get("characters", [])
                char_str = ", ".join(characters) if characters else "Unknown Role"
                lines.append(f"- **{name}** as {char_str}")
            lines.append("")

        if crew:
            lines.append("## Crew\n")
            for department, members in sorted(crew.items()):
                lines.append(f"### {department.title()}\n")
                for member in members:
                    person = member.get("person", {})
                    name = person.get("name", "Unknown")
                    jobs = member.get("jobs", [])
                    jobs_str = ", ".join(jobs) if jobs else "Unknown"
                    lines.append(f"- **{name}** - {jobs_str}")
                lines.append("")

        return "\n".join(lines)
