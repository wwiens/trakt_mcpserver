"""People formatting methods for the Trakt MCP server."""

from models.formatters.utils import (
    MAX_OVERVIEW_LENGTH,
    format_list_items,
    format_title_year,
)
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
        lines: list[str] = [f"# {name}", ""]

        ids = person.get("ids", {})
        if ids:
            lines.append("### Identifiers")
            if trakt_id := ids.get("trakt"):
                lines.append(f"- Trakt: {trakt_id}")
            if slug := ids.get("slug"):
                lines.append(f"- Slug: {slug}")
            if imdb := ids.get("imdb"):
                lines.append(f"- IMDB: {imdb}")
            if tmdb := ids.get("tmdb"):
                lines.append(f"- TMDB: {tmdb}")
            lines.append("")

        if gender := person.get("gender"):
            lines.append(f"- **Gender:** {gender.replace('_', ' ').title()}")

        if birthday := person.get("birthday"):
            lines.append(f"- **Birthday:** {birthday}")

        if death := person.get("death"):
            lines.append(f"- **Death:** {death}")

        if birthplace := person.get("birthplace"):
            lines.append(f"- **Birthplace:** {birthplace}")

        if known_for := person.get("known_for_department"):
            lines.append(f"- **Known For:** {known_for.title()}")

        if homepage := person.get("homepage"):
            lines.append(f"- **Homepage:** {homepage}")

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
                lines.append("")
                lines.append("### Social Media")
                lines.extend(f"- {social}" for social in socials)
                lines.append("")

        if biography := person.get("biography"):
            if len(biography) > MAX_OVERVIEW_LENGTH:
                biography = biography[: MAX_OVERVIEW_LENGTH - 3] + "..."
            lines.append("")
            lines.append("### Biography")
            lines.append("")
            lines.append(biography)

        return "\n".join(lines)

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

        lines: list[str] = ["## Cast", ""]
        for member in members:
            movie = member.get("movie", {})
            title = movie.get("title", "Unknown")
            year = movie.get("year")
            characters = member.get("characters", [])
            char_str = ", ".join(characters) if characters else "Unknown Role"
            title_str = format_title_year(title, year)
            lines.append(f"- **{title_str}** as {char_str}")
        lines.append("")
        return "\n".join(lines)

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

        lines: list[str] = ["## Crew", ""]
        for department, members in sorted(crew.items()):
            lines.append(f"### {department.title()}")
            lines.append("")
            for member in members:
                movie = member.get("movie", {})
                title = movie.get("title", "Unknown")
                year = movie.get("year")
                jobs = member.get("jobs", [])
                jobs_str = ", ".join(jobs) if jobs else "Unknown"
                title_str = format_title_year(title, year)
                lines.append(f"- **{title_str}** - {jobs_str}")
            lines.append("")
        return "\n".join(lines)

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

        lines: list[str] = [f"# Movie Credits for {person_name}", ""]
        cast_section = PeopleFormatters._format_movie_cast_section(
            movie_credits.get("cast", [])
        )
        crew_section = PeopleFormatters._format_movie_crew_section(
            movie_credits.get("crew", {})
        )
        if cast_section:
            lines.append(cast_section)
        if crew_section:
            lines.append(crew_section)
        return "\n".join(lines)

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

        lines: list[str] = ["## Cast", ""]
        for member in members:
            show = member.get("show", {})
            title = show.get("title", "Unknown")
            year = show.get("year")
            characters = member.get("characters", [])
            char_str = ", ".join(characters) if characters else "Unknown Role"
            title_str = format_title_year(title, year)

            extras: list[str] = []
            if episode_count := member.get("episode_count"):
                extras.append(f"{episode_count} episodes")
            if member.get("series_regular"):
                extras.append("series regular")
            extras_str = f" ({', '.join(extras)})" if extras else ""

            lines.append(f"- **{title_str}** as {char_str}{extras_str}")
        lines.append("")
        return "\n".join(lines)

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

        lines: list[str] = ["## Crew", ""]
        for department, members in sorted(crew.items()):
            lines.append(f"### {department.title()}")
            lines.append("")
            for member in members:
                show = member.get("show", {})
                title = show.get("title", "Unknown")
                year = show.get("year")
                jobs = member.get("jobs", [])
                jobs_str = ", ".join(jobs) if jobs else "Unknown"
                title_str = format_title_year(title, year)
                episode_count = member.get("episode_count")
                count_str = (
                    f" ({episode_count} episodes)" if episode_count is not None else ""
                )
                lines.append(f"- **{title_str}** - {jobs_str}{count_str}")
            lines.append("")
        return "\n".join(lines)

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

        lines: list[str] = [f"# Show Credits for {person_name}", ""]
        cast_section = PeopleFormatters._format_show_cast_section(
            show_credits.get("cast", [])
        )
        crew_section = PeopleFormatters._format_show_crew_section(
            show_credits.get("crew", {})
        )
        if cast_section:
            lines.append(cast_section)
        if crew_section:
            lines.append(crew_section)
        return "\n".join(lines)

    @staticmethod
    def format_person_lists(lists: list[ListItemResponse], person_name: str) -> str:
        """Format lists containing a person.

        Args:
            lists: List of list data from Trakt API
            person_name: The person's name

        Returns:
            Formatted markdown text with lists
        """
        return format_list_items(
            lists,
            context=person_name,
            item_type="person",
        )
