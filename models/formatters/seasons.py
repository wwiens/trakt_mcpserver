"""Season formatting methods for the Trakt MCP server."""

from models.formatters.utils import MAX_OVERVIEW_LENGTH
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

        result = f"# {title}\n\n"

        if overview := season.get("overview"):
            result += f"{overview}\n\n"

        result += "### Details\n"
        result += f"- Season Number: {number}\n"

        episode_count = season.get("episode_count")
        if episode_count is not None:
            result += f"- Total Episodes: {episode_count}\n"

        aired_episodes = season.get("aired_episodes")
        if aired_episodes is not None:
            result += f"- Aired Episodes: {aired_episodes}\n"

        if first_aired := season.get("first_aired"):
            result += f"- First Aired: {first_aired}\n"

        rating = season.get("rating")
        if rating is not None:
            votes = season.get("votes", 0)
            result += f"- Rating: {rating:.1f}/10 ({votes} votes)\n"

        ids = season.get("ids", {})
        if trakt_id := ids.get("trakt"):
            result += f"\nTrakt ID: {trakt_id}\n"

        return result

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

        result = f"# Season {season_number} Episodes\n\n"
        result += f"**{len(episodes)} episode(s)**\n\n"

        result += "| # | Title | Rating | Runtime |\n"
        result += "|---|-------|--------|---------|\n"

        for episode in episodes:
            number = episode.get("number", 0)
            title = episode.get("title", "TBA")
            rating = episode.get("rating")
            rating_str = f"{rating:.1f}/10" if rating is not None else "—"
            runtime = episode.get("runtime")
            runtime_str = f"{runtime}m" if runtime else "—"

            result += f"| {number} | {title} | {rating_str} | {runtime_str} |\n"

        return result

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
        result = f"# Ratings for {show_title} - Season {season}\n\n"

        if not ratings:
            return result + "No ratings data available."

        average_rating = ratings.get("rating", 0)
        votes = ratings.get("votes", 0)
        distribution = ratings.get("distribution", {})

        result += f"**Average Rating:** {average_rating:.2f}/10 from {votes} votes\n\n"

        if distribution:
            result += "## Rating Distribution\n\n"
            result += "| Rating | Votes | Percentage |\n"
            result += "|--------|-------|------------|\n"

            for rating in range(10, 0, -1):
                rating_str = str(rating)
                count = distribution.get(rating_str, 0)
                percentage = (count / votes * 100) if votes > 0 else 0
                result += f"| {rating}/10 | {count} | {percentage:.1f}% |\n"

        return result

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

        result = f"# Stats for {show_title} - Season {season}\n\n"

        result += "| Metric | Value |\n"
        result += "|--------|-------|\n"
        result += f"| Watchers | {stats.get('watchers', 0):,} |\n"
        result += f"| Plays | {stats.get('plays', 0):,} |\n"
        result += f"| Collectors | {stats.get('collectors', 0):,} |\n"
        result += f"| Collected Episodes | {stats.get('collected_episodes', 0):,} |\n"
        result += f"| Comments | {stats.get('comments', 0):,} |\n"
        result += f"| Lists | {stats.get('lists', 0):,} |\n"
        result += f"| Votes | {stats.get('votes', 0):,} |\n"

        return result

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

        result = f"## {heading}\n\n"
        for member in members:
            person = member.get("person", {})
            name = person.get("name", "Unknown")
            characters = member.get("characters", [])
            char_str = ", ".join(characters) if characters else "Unknown Role"
            episode_count = member.get("episode_count", 0)
            result += f"- **{name}** as {char_str} ({episode_count} episodes)\n"
        result += "\n"
        return result

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

        result = f"# People for {show_title} - Season {season}\n\n"

        result += SeasonFormatters._format_cast_section(people.get("cast", []), "Cast")
        result += SeasonFormatters._format_cast_section(
            people.get("guest_stars", []), "Guest Stars"
        )

        crew: dict[str, list[CrewMember]] = people.get("crew", {})
        if crew:
            result += "## Crew\n\n"
            for department, members in sorted(crew.items()):
                result += f"### {department.title()}\n\n"
                for member in members:
                    person = member.get("person", {})
                    name = person.get("name", "Unknown")
                    jobs = member.get("jobs", [])
                    jobs_str = ", ".join(jobs) if jobs else "Unknown"
                    episode_count = member.get("episode_count", 0)
                    result += f"- **{name}** - {jobs_str} ({episode_count} episodes)\n"
                result += "\n"

        return result

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
        result = f"# Currently Watching {show_title} - Season {season}\n\n"

        if not users:
            return result + "No one is currently watching this season."

        result += f"**{len(users)} user(s) watching**\n\n"

        for user in users:
            username = user.get("username", "Unknown")
            name = user.get("name", "")
            vip = user.get("vip", False)

            display = f"- **{username}**"
            if name:
                display += f" ({name})"
            if vip:
                display += " [VIP]"
            result += display + "\n"

        return result

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
        result = f"# Translations for {show_title} - Season {season}\n\n"

        if not translations:
            return result + "No translations available."

        result += f"**{len(translations)} translation(s)**\n\n"

        result += "| Language | Country | Title |\n"
        result += "|----------|---------|-------|\n"

        for translation in translations:
            language = translation.get("language", "—")
            country = translation.get("country", "—")
            title = translation.get("title", "—")
            result += f"| {language} | {country} | {title} |\n"

        return result

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
        result = f"# Lists Containing {show_title} - Season {season}\n\n"

        if not lists:
            return result + "No lists found containing this season."

        result += f"**{len(lists)} list(s)**\n\n"

        for list_item in lists:
            name = list_item.get("name", "Unknown List")
            item_count = list_item.get("item_count", 0)
            likes = list_item.get("likes", 0)
            user = list_item.get("user", {})
            username = user.get("username", "Unknown")

            result += f"- **{name}** by {username}"
            result += f" ({item_count} items, {likes} likes)\n"

            if description := list_item.get("description"):
                if len(description) > MAX_OVERVIEW_LENGTH:
                    description = description[: MAX_OVERVIEW_LENGTH - 3] + "..."
                result += f"  {description}\n"

        return result
