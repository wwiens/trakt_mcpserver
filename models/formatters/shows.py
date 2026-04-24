"""Show formatting methods for the Trakt MCP server."""

from models.formatters.utils import (
    MAX_OVERVIEW_LENGTH,
    format_cast_section,
    format_crew_section,
    format_media_list,
    format_pagination_header,
    format_rating_distribution,
    format_title_year,
)
from models.types import (
    AnticipatedShowWrapper,
    CastMember,
    FavoritedShowWrapper,
    PeopleResponse,
    PlayedShowWrapper,
    SeasonResponse,
    ShowResponse,
    TraktRating,
    TrendingWrapper,
    WatchedShowWrapper,
)
from models.types.pagination import PaginatedResponse


class ShowFormatters:
    """Helper class for formatting show-related data for MCP responses."""

    @staticmethod
    def format_trending_shows(
        data: list[TrendingWrapper] | PaginatedResponse[TrendingWrapper],
    ) -> str:
        """Format trending shows data for MCP resource."""
        return format_media_list(
            data,
            heading="Trending Shows on Trakt",
            media_key="show",
            format_metric=lambda item: f"{item.get('watchers', 0)} watchers",
        )

    @staticmethod
    def format_popular_shows(
        data: list[ShowResponse] | PaginatedResponse[ShowResponse],
    ) -> str:
        """Format popular shows data for MCP resource."""
        return format_media_list(
            data,
            heading="Popular Shows on Trakt",
            media_key=None,
        )

    @staticmethod
    def format_favorited_shows(
        data: list[FavoritedShowWrapper] | PaginatedResponse[FavoritedShowWrapper],
    ) -> str:
        """Format favorited shows data for MCP resource."""
        return format_media_list(
            data,
            heading="Most Favorited Shows on Trakt",
            media_key="show",
            format_metric=lambda item: (
                f"Favorited by {item.get('user_count', 0)} users"
            ),
        )

    @staticmethod
    def format_played_shows(
        data: list[PlayedShowWrapper] | PaginatedResponse[PlayedShowWrapper],
    ) -> str:
        """Format played shows data for MCP resource."""
        return format_media_list(
            data,
            heading="Most Played Shows on Trakt",
            media_key="show",
            format_metric=lambda item: (
                f"{item.get('watcher_count', 0)} watchers, "
                f"{item.get('play_count', 0)} plays"
            ),
        )

    @staticmethod
    def format_watched_shows(
        data: list[WatchedShowWrapper] | PaginatedResponse[WatchedShowWrapper],
    ) -> str:
        """Format watched shows data for MCP resource."""
        return format_media_list(
            data,
            heading="Most Watched Shows on Trakt",
            media_key="show",
            format_metric=lambda item: (
                f"Watched by {item.get('watcher_count', 0)} users"
            ),
        )

    @staticmethod
    def format_anticipated_shows(
        data: list[AnticipatedShowWrapper] | PaginatedResponse[AnticipatedShowWrapper],
    ) -> str:
        """Format anticipated shows data for MCP resource."""
        return format_media_list(
            data,
            heading="Most Anticipated Shows on Trakt",
            media_key="show",
            format_metric=lambda item: f"On {item.get('list_count', 0)} lists",
        )

    @staticmethod
    def format_show_ratings(
        ratings: TraktRating, show_title: str = "Unknown show"
    ) -> str:
        """Format show ratings data for MCP resource."""
        lines: list[str] = [f"# Ratings for {show_title}", ""]

        if not ratings:
            return f"# Ratings for {show_title}\n\nNo ratings data available."

        average_rating = ratings.get("rating", 0)
        votes = ratings.get("votes", 0)
        distribution = ratings.get("distribution", {})

        lines.append(f"**Average Rating:** {average_rating:.2f}/10 from {votes} votes")
        lines.append("")

        if distribution:
            lines.append(format_rating_distribution(distribution, votes))

        return "\n".join(lines)

    @staticmethod
    def format_show_summary(show: ShowResponse) -> str:
        """Format basic show summary data."""
        if not show:
            return "No show data available."

        title = show.get("title", "Unknown")
        year = show.get("year", "")
        title_str = format_title_year(title, year)
        ids = show.get("ids", {})
        trakt_id = ids.get("trakt", "Unknown")

        lines: list[str] = [f"## {title_str}", ""]
        lines.append(f"Trakt ID: {trakt_id}")

        return "\n".join(lines)

    @staticmethod
    def format_show_extended(show: ShowResponse) -> str:
        """Format extended show details data."""
        if not show:
            return "No show data available."

        title = show.get("title", "Unknown")
        year = show.get("year", "")
        title_str = format_title_year(title, year)
        status = show.get("status", "unknown")
        tagline = show.get("tagline", "")
        overview = show.get("overview", "No overview available.")
        ids = show.get("ids", {})
        trakt_id = ids.get("trakt", "Unknown")

        lines: list[str] = [f"## {title_str} - {status.title().replace('_', ' ')}"]

        if tagline:
            lines.append(f"*{tagline}*")

        lines.append("")
        lines.append(overview)
        lines.append("")
        lines.append("### Production Details")
        lines.append(f"- Status: {status.replace('_', ' ')}")

        if runtime := show.get("runtime"):
            lines.append(f"- Runtime: {runtime} minutes")

        if certification := show.get("certification"):
            lines.append(f"- Certification: {certification}")

        if network := show.get("network"):
            lines.append(f"- Network: {network}")

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
                lines.append(air_time_str)

        if aired_episodes := show.get("aired_episodes"):
            lines.append(f"- Aired Episodes: {aired_episodes}")

        if country := show.get("country"):
            lines.append(f"- Country: {country.upper()}")

        if genres := show.get("genres"):
            genres_str = ", ".join(genres)
            lines.append(f"- Genres: {genres_str}")

        if languages := show.get("languages"):
            languages_str = ", ".join(languages)
            lines.append(f"- Languages: {languages_str}")

        if homepage := show.get("homepage"):
            lines.append(f"- Homepage: {homepage}")

        lines.append("")
        lines.append("### Ratings & Engagement")

        rating = show.get("rating", 0)
        votes = show.get("votes", 0)
        lines.append(f"- Rating: {rating:.1f}/10 ({votes} votes)")

        if comment_count := show.get("comment_count"):
            lines.append(f"- Comments: {comment_count}")

        lines.append("")
        lines.append(f"Trakt ID: {trakt_id}")

        return "\n".join(lines)

    @staticmethod
    def format_show_seasons(seasons: list[SeasonResponse]) -> str:
        """Format show seasons data for MCP response."""
        if not seasons:
            return "No seasons data available."

        lines: list[str] = ["# Seasons", ""]
        lines.append(f"**{len(seasons)} season(s)**")
        lines.append("")
        lines.append("| Season | Title | Episodes | Aired | Rating |")
        lines.append("|--------|-------|----------|-------|--------|")

        for season in seasons:
            number = season.get("number", 0)
            title = season.get("title", "")
            if number == 0 and not title:
                title = "Specials"
            elif not title:
                title = f"Season {number}"

            episode_count = season.get("episode_count", "—")
            aired_episodes = season.get("aired_episodes", "—")
            rating = season.get("rating")
            rating_str = f"{rating:.1f}/10" if rating is not None else "—"

            row = (
                f"| {number} | {title} | {episode_count}"
                f" | {aired_episodes} | {rating_str} |"
            )
            lines.append(row)

        return "\n".join(lines)

    @staticmethod
    def format_related_shows(
        data: list[ShowResponse] | PaginatedResponse[ShowResponse],
    ) -> str:
        """Format related shows data for MCP resource."""
        lines: list[str] = ["# Related Shows", ""]

        if isinstance(data, PaginatedResponse):
            lines.append(format_pagination_header(data).rstrip("\n"))
            lines.append("")
            shows = data.data
        else:
            shows = data

        if not shows:
            return "# Related Shows\n\nNo related shows found.\n"

        for show in shows:
            title = show.get("title", "Unknown")
            year = show.get("year", "")
            title_str = format_title_year(title, year)

            lines.append(f"- **{title_str}**")

            if overview := show.get("overview"):
                if len(overview) > MAX_OVERVIEW_LENGTH:
                    overview = overview[: MAX_OVERVIEW_LENGTH - 3] + "..."
                lines.append(f"  {overview}")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_show_people(people: PeopleResponse, show_title: str) -> str:
        """Format show cast and crew data."""
        if not people:
            return f"# People for {show_title}\n\nNo people data available."

        cast: list[CastMember] = people.get("cast", [])
        guest_stars: list[CastMember] = people.get("guest_stars", [])
        crew = people.get("crew", {})

        if not cast and not guest_stars and not crew:
            return f"# People for {show_title}\n\nNo people data available."

        lines: list[str] = [f"# People for {show_title}", ""]

        cast_section = format_cast_section(cast, "Cast", include_episode_count=True)
        if cast_section:
            lines.append(cast_section)
        guest_section = format_cast_section(
            guest_stars, "Guest Stars", include_episode_count=True
        )
        if guest_section:
            lines.append(guest_section)
        crew_section = format_crew_section(crew, include_episode_count=True)
        if crew_section:
            lines.append(crew_section)

        return "\n".join(lines)
