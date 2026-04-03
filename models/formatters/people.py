"""People formatting methods for the Trakt MCP server."""

from models.formatters.utils import MAX_OVERVIEW_LENGTH
from models.types import (
    ListItemResponse,
    PersonMovieCastCredit,
    PersonMovieCreditsResponse,
    PersonMovieCrewCredit,
    PersonResponse,
    PersonShowCastCredit,
    PersonShowCreditsResponse,
    PersonShowCrewCredit,
)


class PeopleFormatters:
    """Helper class for formatting people-related data for MCP responses."""

    @staticmethod
    def format_person_summary(person: PersonResponse) -> str:
        """Format person details.

        Args:
            person: Person data from Trakt API

        Returns:
            Formatted markdown text with person details
        """
        if not person:
            return "# Person\n\nNo person data available."

        name = person.get("name", "Unknown")
        result = f"# {name}\n\n"

        ids = person.get("ids", {})
        if ids:
            result += "### Identifiers\n"
            if trakt_id := ids.get("trakt"):
                result += f"- Trakt: {trakt_id}\n"
            if slug := ids.get("slug"):
                result += f"- Slug: {slug}\n"
            if imdb := ids.get("imdb"):
                result += f"- IMDB: {imdb}\n"
            if tmdb := ids.get("tmdb"):
                result += f"- TMDB: {tmdb}\n"
            result += "\n"

        if gender := person.get("gender"):
            result += f"- **Gender:** {gender.replace('_', ' ').title()}\n"

        if birthday := person.get("birthday"):
            result += f"- **Birthday:** {birthday}\n"

        if death := person.get("death"):
            result += f"- **Death:** {death}\n"

        if birthplace := person.get("birthplace"):
            result += f"- **Birthplace:** {birthplace}\n"

        if known_for := person.get("known_for_department"):
            result += f"- **Known For:** {known_for.title()}\n"

        if homepage := person.get("homepage"):
            result += f"- **Homepage:** {homepage}\n"

        social_ids = person.get("social_ids", {})
        if social_ids:
            socials: list[str] = []
            if twitter := social_ids.get("twitter"):
                socials.append(f"Twitter: @{twitter}")
            if facebook := social_ids.get("facebook"):
                socials.append(f"Facebook: {facebook}")
            if instagram := social_ids.get("instagram"):
                socials.append(f"Instagram: @{instagram}")
            if wikipedia := social_ids.get("wikipedia"):
                socials.append(f"Wikipedia: {wikipedia}")
            if socials:
                result += "\n### Social Media\n"
                for social in socials:
                    result += f"- {social}\n"
                result += "\n"

        if biography := person.get("biography"):
            if len(biography) > MAX_OVERVIEW_LENGTH:
                biography = biography[: MAX_OVERVIEW_LENGTH - 3] + "..."
            result += f"\n### Biography\n\n{biography}\n"

        return result

    @staticmethod
    def _format_movie_cast_section(
        members: list[PersonMovieCastCredit],
    ) -> str:
        """Format person's movie cast credits.

        Args:
            members: List of movie cast credits

        Returns:
            Formatted markdown section
        """
        if not members:
            return ""

        result = "## Cast\n\n"
        for member in members:
            movie = member.get("movie", {})
            title = movie.get("title", "Unknown")
            year = movie.get("year")
            characters = member.get("characters", [])
            char_str = ", ".join(characters) if characters else "Unknown Role"
            year_str = f" ({year})" if year else ""
            result += f"- **{title}**{year_str} as {char_str}\n"
        result += "\n"
        return result

    @staticmethod
    def _format_movie_crew_section(
        crew: dict[str, list[PersonMovieCrewCredit]],
    ) -> str:
        """Format person's movie crew credits.

        Args:
            crew: Crew credits grouped by department

        Returns:
            Formatted markdown section
        """
        if not crew:
            return ""

        result = "## Crew\n\n"
        for department, members in sorted(crew.items()):
            result += f"### {department.title()}\n\n"
            for member in members:
                movie = member.get("movie", {})
                title = movie.get("title", "Unknown")
                year = movie.get("year")
                jobs = member.get("jobs", [])
                jobs_str = ", ".join(jobs) if jobs else "Unknown"
                year_str = f" ({year})" if year else ""
                result += f"- **{title}**{year_str} - {jobs_str}\n"
            result += "\n"
        return result

    @staticmethod
    def format_person_movie_credits(
        movie_credits: PersonMovieCreditsResponse, person_name: str
    ) -> str:
        """Format person's movie credits.

        Args:
            movie_credits: Movie credits from Trakt API
            person_name: The person's name

        Returns:
            Formatted markdown text with movie credits
        """
        if not movie_credits:
            return f"# Movie Credits for {person_name}\n\nNo movie credits available."

        result = f"# Movie Credits for {person_name}\n\n"
        result += PeopleFormatters._format_movie_cast_section(
            movie_credits.get("cast", [])
        )
        result += PeopleFormatters._format_movie_crew_section(
            movie_credits.get("crew", {})
        )
        return result

    @staticmethod
    def _format_show_cast_section(
        members: list[PersonShowCastCredit],
    ) -> str:
        """Format person's show cast credits.

        Args:
            members: List of show cast credits

        Returns:
            Formatted markdown section
        """
        if not members:
            return ""

        result = "## Cast\n\n"
        for member in members:
            show = member.get("show", {})
            title = show.get("title", "Unknown")
            year = show.get("year")
            characters = member.get("characters", [])
            char_str = ", ".join(characters) if characters else "Unknown Role"
            year_str = f" ({year})" if year else ""

            extras: list[str] = []
            if episode_count := member.get("episode_count"):
                extras.append(f"{episode_count} episodes")
            if member.get("series_regular"):
                extras.append("series regular")
            extras_str = f" ({', '.join(extras)})" if extras else ""

            result += f"- **{title}**{year_str} as {char_str}{extras_str}\n"
        result += "\n"
        return result

    @staticmethod
    def _format_show_crew_section(
        crew: dict[str, list[PersonShowCrewCredit]],
    ) -> str:
        """Format person's show crew credits.

        Args:
            crew: Crew credits grouped by department

        Returns:
            Formatted markdown section
        """
        if not crew:
            return ""

        result = "## Crew\n\n"
        for department, members in sorted(crew.items()):
            result += f"### {department.title()}\n\n"
            for member in members:
                show = member.get("show", {})
                title = show.get("title", "Unknown")
                year = show.get("year")
                jobs = member.get("jobs", [])
                jobs_str = ", ".join(jobs) if jobs else "Unknown"
                year_str = f" ({year})" if year else ""
                episode_count = member.get("episode_count")
                count_str = (
                    f" ({episode_count} episodes)" if episode_count is not None else ""
                )
                result += f"- **{title}**{year_str} - {jobs_str}{count_str}\n"
            result += "\n"
        return result

    @staticmethod
    def format_person_show_credits(
        show_credits: PersonShowCreditsResponse, person_name: str
    ) -> str:
        """Format person's show credits.

        Args:
            show_credits: Show credits from Trakt API
            person_name: The person's name

        Returns:
            Formatted markdown text with show credits
        """
        if not show_credits:
            return f"# Show Credits for {person_name}\n\nNo show credits available."

        result = f"# Show Credits for {person_name}\n\n"
        result += PeopleFormatters._format_show_cast_section(
            show_credits.get("cast", [])
        )
        result += PeopleFormatters._format_show_crew_section(
            show_credits.get("crew", {})
        )
        return result

    @staticmethod
    def format_person_lists(lists: list[ListItemResponse], person_name: str) -> str:
        """Format lists containing a person.

        Args:
            lists: List of list data from Trakt API
            person_name: The person's name

        Returns:
            Formatted markdown text with lists
        """
        result = f"# Lists Containing {person_name}\n\n"

        if not lists:
            return result + "No lists found containing this person."

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
