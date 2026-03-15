"""Episode formatting methods for the Trakt MCP server."""

from models.formatters.utils import MAX_OVERVIEW_LENGTH
from models.types import (
    CastMember,
    CrewMember,
    EpisodeResponse,
    ListItemResponse,
    PeopleResponse,
    StatsResponse,
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

        result = f"# {show_title} - S{season:02d}E{number:02d}: {title}\n\n"

        if overview := episode.get("overview"):
            if len(overview) > MAX_OVERVIEW_LENGTH:
                overview = overview[: MAX_OVERVIEW_LENGTH - 3] + "..."
            result += f"{overview}\n\n"

        result += "### Details\n"

        if first_aired := episode.get("first_aired"):
            result += f"- First Aired: {first_aired}\n"

        runtime = episode.get("runtime")
        if runtime is not None:
            result += f"- Runtime: {runtime} minutes\n"

        rating = episode.get("rating")
        if rating is not None:
            votes = episode.get("votes", 0)
            result += f"- Rating: {rating:.1f}/10 ({votes} votes)\n"

        comment_count = episode.get("comment_count")
        if comment_count is not None:
            result += f"- Comments: {comment_count}\n"

        if translations := episode.get("available_translations"):
            result += f"- Available Translations: {', '.join(translations)}\n"

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
            result += f"\n**IDs:** {' | '.join(id_parts)}\n"

        return result

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
        result = f"# Ratings for {show_title} - S{season:02d}E{episode:02d}\n\n"

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
    def format_episode_stats(
        stats: StatsResponse, show_title: str, season: int, episode: int
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

        result = f"# Stats for {show_title} - S{season:02d}E{episode:02d}\n\n"

        result += "| Metric | Value |\n"
        result += "|--------|-------|\n"
        result += f"| Watchers | {stats.get('watchers', 0):,} |\n"
        result += f"| Plays | {stats.get('plays', 0):,} |\n"
        result += f"| Collectors | {stats.get('collectors', 0):,} |\n"
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

        result = f"# People for {show_title} - S{season:02d}E{episode:02d}\n\n"

        result += EpisodeFormatters._format_cast_section(people.get("cast", []), "Cast")
        result += EpisodeFormatters._format_cast_section(
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
        result = f"# Currently Watching {show_title} - S{season:02d}E{episode:02d}\n\n"

        if not users:
            return result + "No one is currently watching this episode."

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
        result = f"# Translations for {show_title} - S{season:02d}E{episode:02d}\n\n"

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
        result = f"# Lists Containing {show_title} - S{season:02d}E{episode:02d}\n\n"

        if not lists:
            return result + "No lists found containing this episode."

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
