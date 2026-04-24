"""Episode formatting methods for the Trakt MCP server."""

from models.formatters.utils import (
    MAX_OVERVIEW_LENGTH,
    format_cast_section,
    format_list_items,
    format_rating_distribution,
)
from models.types import (
    CrewMember,
    EpisodeResponse,
    ListItemResponse,
    PeopleResponse,
    SeasonStatsResponse,
    TraktRating,
    TranslationResponse,
    UserResponse,
)


class EpisodeFormatters:
    """Helper class for formatting episode-related data for MCP responses."""

    @staticmethod
    def format_episode_summary(episode: EpisodeResponse, show_title: str) -> str:
        """Format detailed single episode data.

        Args:
            episode: Episode data from Trakt API
            show_title: The title of the show

        Returns:
            Formatted markdown text with episode details
        """
        if not episode:
            return f"# {show_title}\n\nNo episode data available."

        season = episode.get("season", 0)
        number = episode.get("number", 0)
        title = episode.get("title", "TBA")

        lines: list[str] = [f"# {show_title} - S{season:02d}E{number:02d}: {title}", ""]

        if overview := episode.get("overview"):
            if len(overview) > MAX_OVERVIEW_LENGTH:
                overview = overview[: MAX_OVERVIEW_LENGTH - 3] + "..."
            lines.append(overview)
            lines.append("")

        lines.append("### Details")

        if first_aired := episode.get("first_aired"):
            lines.append(f"- First Aired: {first_aired}")

        runtime = episode.get("runtime")
        if runtime is not None:
            lines.append(f"- Runtime: {runtime} minutes")

        rating = episode.get("rating")
        if rating is not None:
            votes = episode.get("votes", 0)
            lines.append(f"- Rating: {rating:.1f}/10 ({votes} votes)")

        comment_count = episode.get("comment_count")
        if comment_count is not None:
            lines.append(f"- Comments: {comment_count}")

        if translations := episode.get("available_translations"):
            lines.append(f"- Available Translations: {', '.join(translations)}")

        ids = episode.get("ids", {})
        id_parts: list[str] = []
        if trakt_id := ids.get("trakt"):
            id_parts.append(f"Trakt: {trakt_id}")
        if imdb_id := ids.get("imdb"):
            id_parts.append(f"IMDB: {imdb_id}")
        if tmdb_id := ids.get("tmdb"):
            id_parts.append(f"TMDB: {tmdb_id}")
        if tvdb_id := ids.get("tvdb"):
            id_parts.append(f"TVDB: {tvdb_id}")
        if id_parts:
            lines.append("")
            lines.append(f"**IDs:** {' | '.join(id_parts)}")

        return "\n".join(lines)

    @staticmethod
    def format_episode_ratings(
        ratings: TraktRating, show_title: str, season: int, episode: int
    ) -> str:
        """Format episode ratings data.

        Args:
            ratings: The ratings data from Trakt API
            show_title: The title of the show
            season: Season number
            episode: Episode number

        Returns:
            Formatted markdown text with ratings information
        """
        heading = f"# Ratings for {show_title} - S{season:02d}E{episode:02d}"
        lines: list[str] = [heading, ""]

        if not ratings:
            return f"{heading}\n\nNo ratings data available."

        average_rating = ratings.get("rating", 0)
        votes = ratings.get("votes", 0)
        distribution = ratings.get("distribution", {})

        lines.append(f"**Average Rating:** {average_rating:.2f}/10 from {votes} votes")
        lines.append("")

        if distribution:
            lines.append(format_rating_distribution(distribution, votes))

        return "\n".join(lines)

    @staticmethod
    def format_episode_stats(
        stats: SeasonStatsResponse, show_title: str, season: int, episode: int
    ) -> str:
        """Format episode statistics data.

        Args:
            stats: Episode statistics from Trakt API
            show_title: The title of the show
            season: Season number
            episode: Episode number

        Returns:
            Formatted markdown text with statistics
        """
        if not stats:
            return (
                f"# Stats for {show_title} - S{season:02d}E{episode:02d}\n\n"
                "No statistics available."
            )

        lines: list[str] = [
            f"# Stats for {show_title} - S{season:02d}E{episode:02d}",
            "",
        ]

        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Watchers | {stats.get('watchers', 0):,} |")
        lines.append(f"| Plays | {stats.get('plays', 0):,} |")
        lines.append(f"| Collectors | {stats.get('collectors', 0):,} |")
        lines.append(f"| Collected Episodes | {stats.get('collected_episodes', 0):,} |")
        lines.append(f"| Comments | {stats.get('comments', 0):,} |")
        lines.append(f"| Lists | {stats.get('lists', 0):,} |")
        lines.append(f"| Votes | {stats.get('votes', 0):,} |")

        return "\n".join(lines)

    @staticmethod
    def format_episode_people(
        people: PeopleResponse, show_title: str, season: int, episode: int
    ) -> str:
        """Format episode cast and crew data.

        Args:
            people: People data from Trakt API
            show_title: The title of the show
            season: Season number
            episode: Episode number

        Returns:
            Formatted markdown text with cast and crew
        """
        if not people:
            return (
                f"# People for {show_title} - S{season:02d}E{episode:02d}\n\n"
                "No people data available."
            )

        cast = people.get("cast", [])
        guest_stars = people.get("guest_stars", [])
        crew: dict[str, list[CrewMember]] = people.get("crew", {})

        if not cast and not guest_stars and not crew:
            return (
                f"# People for {show_title} - S{season:02d}E{episode:02d}\n\n"
                "No people data available."
            )

        lines: list[str] = [
            f"# People for {show_title} - S{season:02d}E{episode:02d}",
            "",
        ]

        cast_section = format_cast_section(cast, "Cast")
        if cast_section:
            lines.append(cast_section)
        guest_section = format_cast_section(guest_stars, "Guest Stars")
        if guest_section:
            lines.append(guest_section)
        if crew:
            lines.append("## Crew")
            lines.append("")
            for department, members in sorted(crew.items()):
                lines.append(f"### {department.title()}")
                lines.append("")
                for member in members:
                    person = member.get("person", {})
                    name = person.get("name", "Unknown")
                    jobs = member.get("jobs", [])
                    jobs_str = ", ".join(jobs) if jobs else "Unknown"
                    lines.append(f"- **{name}** - {jobs_str}")
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_episode_watching(
        users: list[UserResponse], show_title: str, season: int, episode: int
    ) -> str:
        """Format users currently watching an episode.

        Args:
            users: List of user data from Trakt API
            show_title: The title of the show
            season: Season number
            episode: Episode number

        Returns:
            Formatted markdown text with user list
        """
        heading = f"# Currently Watching {show_title} - S{season:02d}E{episode:02d}"

        if not users:
            return f"{heading}\n\nNo one is currently watching this episode."

        lines: list[str] = [heading, ""]
        lines.append(f"**{len(users)} user(s) watching**")
        lines.append("")

        for user in users:
            username = user.get("username", "Unknown")
            name = user.get("name", "")
            vip = user.get("vip", False)

            display = f"- **{username}**"
            if name:
                display += f" ({name})"
            if vip:
                display += " [VIP]"
            lines.append(display)

        return "\n".join(lines)

    @staticmethod
    def format_episode_translations(
        translations: list[TranslationResponse],
        show_title: str,
        season: int,
        episode: int,
    ) -> str:
        """Format episode translation data.

        Args:
            translations: List of translation data from Trakt API
            show_title: The title of the show
            season: Season number
            episode: Episode number

        Returns:
            Formatted markdown text with translations
        """
        heading = f"# Translations for {show_title} - S{season:02d}E{episode:02d}"

        if not translations:
            return f"{heading}\n\nNo translations available."

        lines: list[str] = [heading, ""]
        lines.append(f"**{len(translations)} translation(s)**")
        lines.append("")
        lines.append("| Language | Country | Title |")
        lines.append("|----------|---------|-------|")

        for translation in translations:
            language = translation.get("language", "—")
            country = translation.get("country", "—")
            title = translation.get("title", "—")
            lines.append(f"| {language} | {country} | {title} |")

        return "\n".join(lines)

    @staticmethod
    def format_episode_lists(
        lists: list[ListItemResponse],
        show_title: str,
        season: int,
        episode: int,
    ) -> str:
        """Format lists containing an episode.

        Args:
            lists: List of list data from Trakt API
            show_title: The title of the show
            season: Season number
            episode: Episode number

        Returns:
            Formatted markdown text with lists
        """
        return format_list_items(
            lists,
            context=f"{show_title} - S{season:02d}E{episode:02d}",
            item_type="episode",
        )
