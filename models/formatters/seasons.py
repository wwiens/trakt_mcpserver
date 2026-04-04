"""Season formatting methods for the Trakt MCP server."""

from models.formatters.utils import (
    format_list_items,
    format_rating_distribution,
)
from models.types import (
    CastMember,
    CrewMember,
    EpisodeResponse,
    ListItemResponse,
    PeopleResponse,
    SeasonResponse,
    SeasonStatsResponse,
    TraktRating,
    TranslationResponse,
    UserResponse,
)


class SeasonFormatters:
    """Helper class for formatting season-related data for MCP responses."""

    @staticmethod
    def format_season_info(season: SeasonResponse) -> str:
        """Format detailed single season data.

        Args:
            season: Season data from Trakt API

        Returns:
            Formatted markdown text with season details
        """
        if not season:
            return "No season data available."

        number = season.get("number", 0)
        title = season.get("title", "")
        if number == 0 and not title:
            title = "Specials"
        elif not title:
            title = f"Season {number}"

        lines: list[str] = [f"# {title}"]
        lines.append("")

        if overview := season.get("overview"):
            lines.append(overview)
            lines.append("")

        lines.append("### Details")
        lines.append(f"- Season Number: {number}")

        episode_count = season.get("episode_count")
        if episode_count is not None:
            lines.append(f"- Total Episodes: {episode_count}")

        aired_episodes = season.get("aired_episodes")
        if aired_episodes is not None:
            lines.append(f"- Aired Episodes: {aired_episodes}")

        if first_aired := season.get("first_aired"):
            lines.append(f"- First Aired: {first_aired}")

        rating = season.get("rating")
        if rating is not None:
            votes = season.get("votes", 0)
            lines.append(f"- Rating: {rating:.1f}/10 ({votes} votes)")

        ids = season.get("ids", {})
        if trakt_id := ids.get("trakt"):
            lines.append("")
            lines.append(f"Trakt ID: {trakt_id}")

        return "\n".join(lines)

    @staticmethod
    def format_season_episodes(
        episodes: list[EpisodeResponse], season_number: int
    ) -> str:
        """Format episode list for a season.

        Args:
            episodes: List of episode data from Trakt API
            season_number: The season number for context

        Returns:
            Formatted markdown text with episode details
        """
        if not episodes:
            return f"# Season {season_number} Episodes\n\nNo episodes available."

        lines: list[str] = [f"# Season {season_number} Episodes\n"]
        lines.append(f"**{len(episodes)} episode(s)**\n")
        lines.append("| # | Title | Rating | Runtime |")
        lines.append("|---|-------|--------|---------|")

        for episode in episodes:
            number = episode.get("number", 0)
            title = episode.get("title", "TBA")
            rating = episode.get("rating")
            rating_str = f"{rating:.1f}/10" if rating is not None else "—"
            runtime = episode.get("runtime")
            runtime_str = f"{runtime}m" if runtime is not None else "—"

            lines.append(f"| {number} | {title} | {rating_str} | {runtime_str} |")

        return "\n".join(lines)

    @staticmethod
    def format_season_ratings(
        ratings: TraktRating, show_title: str, season: int
    ) -> str:
        """Format season ratings data.

        Args:
            ratings: The ratings data from Trakt API
            show_title: The title of the show
            season: Season number

        Returns:
            Formatted markdown text with ratings information
        """
        heading = f"# Ratings for {show_title} - Season {season}\n"
        lines: list[str] = [heading]

        if not ratings:
            return f"{heading}\nNo ratings data available."

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
    def format_season_stats(
        stats: SeasonStatsResponse, show_title: str, season: int
    ) -> str:
        """Format season statistics data.

        Args:
            stats: Season statistics from Trakt API
            show_title: The title of the show
            season: Season number

        Returns:
            Formatted markdown text with statistics
        """
        if not stats:
            return (
                f"# Stats for {show_title} - Season {season}\n\n"
                "No statistics available."
            )

        lines: list[str] = [f"# Stats for {show_title} - Season {season}\n"]

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
    def _format_cast_section(members: list[CastMember], heading: str) -> str:
        """Format a cast or guest stars section.

        Args:
            members: List of cast member data
            heading: Section heading (e.g., "Cast", "Guest Stars")

        Returns:
            Formatted markdown section, empty string if no members
        """
        if not members:
            return ""

        lines: list[str] = [f"## {heading}\n"]
        for member in members:
            person = member.get("person", {})
            name = person.get("name", "Unknown")
            characters = member.get("characters", [])
            char_str = ", ".join(characters) if characters else "Unknown Role"
            episode_count = member.get("episode_count")
            count_str = (
                f" ({episode_count} episodes)" if episode_count is not None else ""
            )
            lines.append(f"- **{name}** as {char_str}{count_str}")
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def format_season_people(
        people: PeopleResponse, show_title: str, season: int
    ) -> str:
        """Format season cast and crew data.

        Args:
            people: People data from Trakt API
            show_title: The title of the show
            season: Season number

        Returns:
            Formatted markdown text with cast and crew
        """
        if not people:
            return (
                f"# People for {show_title} - Season {season}\n\n"
                "No people data available."
            )

        lines: list[str] = [f"# People for {show_title} - Season {season}\n"]

        cast_section = SeasonFormatters._format_cast_section(
            people.get("cast", []), "Cast"
        )
        if cast_section:
            lines.append(cast_section)
        guest_section = SeasonFormatters._format_cast_section(
            people.get("guest_stars", []), "Guest Stars"
        )
        if guest_section:
            lines.append(guest_section)

        crew: dict[str, list[CrewMember]] = people.get("crew", {})
        if crew:
            lines.append("## Crew\n")
            for department, members in sorted(crew.items()):
                lines.append(f"### {department.title()}\n")
                for member in members:
                    person = member.get("person", {})
                    name = person.get("name", "Unknown")
                    jobs = member.get("jobs", [])
                    jobs_str = ", ".join(jobs) if jobs else "Unknown"
                    episode_count = member.get("episode_count")
                    count_str = (
                        f" ({episode_count} episodes)"
                        if episode_count is not None
                        else ""
                    )
                    lines.append(f"- **{name}** - {jobs_str}{count_str}")
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_season_watching(
        users: list[UserResponse], show_title: str, season: int
    ) -> str:
        """Format users currently watching a season.

        Args:
            users: List of user data from Trakt API
            show_title: The title of the show
            season: Season number

        Returns:
            Formatted markdown text with user list
        """
        heading = f"# Currently Watching {show_title} - Season {season}\n"

        if not users:
            return f"{heading}\nNo one is currently watching this season."

        lines: list[str] = [heading]
        lines.append(f"**{len(users)} user(s) watching**\n")

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
    def format_season_translations(
        translations: list[TranslationResponse],
        show_title: str,
        season: int,
    ) -> str:
        """Format season translation data.

        Args:
            translations: List of translation data from Trakt API
            show_title: The title of the show
            season: Season number

        Returns:
            Formatted markdown text with translations
        """
        heading = f"# Translations for {show_title} - Season {season}\n"

        if not translations:
            return f"{heading}\nNo translations available."

        lines: list[str] = [heading]
        lines.append(f"**{len(translations)} translation(s)**\n")
        lines.append("| Language | Country | Title |")
        lines.append("|----------|---------|-------|")

        for translation in translations:
            language = translation.get("language", "—")
            country = translation.get("country", "—")
            title = translation.get("title", "—")
            lines.append(f"| {language} | {country} | {title} |")

        return "\n".join(lines)

    @staticmethod
    def format_season_lists(
        lists: list[ListItemResponse], show_title: str, season: int
    ) -> str:
        """Format lists containing a season.

        Args:
            lists: List of list data from Trakt API
            show_title: The title of the show
            season: Season number

        Returns:
            Formatted markdown text with lists
        """
        return format_list_items(
            lists,
            context=f"{show_title} - Season {season}",
            item_type="season",
        )
