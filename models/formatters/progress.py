"""Progress formatting methods for the Trakt MCP server."""

from models.progress.playback import PlaybackProgressResponse
from models.progress.show_progress import ShowProgressResponse
from utils.formatting import format_iso_timestamp


class ProgressFormatters:
    """Helper class for formatting progress data for MCP responses."""

    @staticmethod
    def format_show_progress(
        data: ShowProgressResponse, show_id: str, verbose: bool = False
    ) -> str:
        """Format show watched progress as markdown.

        Args:
            data: Show progress response from API
            show_id: The show ID that was queried
            verbose: Show episode-by-episode watch dates (default: False)

        Returns:
            Formatted markdown text with show progress details
        """
        aired = data["aired"]
        completed = data["completed"]
        percentage = (completed / aired * 100) if aired > 0 else 0

        result = f"# Show Progress: {show_id}\n\n"
        result += "## Overall Progress\n\n"
        result += f"- **Watched:** {completed}/{aired} episodes ({percentage:.1f}%)\n"

        last_watched = data.get("last_watched_at")
        if last_watched:
            result += f"- **Last Watched:** {format_iso_timestamp(last_watched)}\n"

        reset_at = data.get("reset_at")
        if reset_at:
            result += f"- **Progress Reset At:** {format_iso_timestamp(reset_at)}\n"

        result += "\n"

        next_episode = data.get("next_episode")
        if next_episode:
            result += "## Up Next\n\n"
            season = next_episode.get("season", 0)
            number = next_episode.get("number", 0)
            title = next_episode.get("title", "")
            episode_label = f"S{season:02d}E{number:02d}"
            if title:
                episode_label += f": {title}"
            result += f"- **{episode_label}**\n\n"

        last_episode = data.get("last_episode")
        if last_episode:
            result += "## Last Watched\n\n"
            season = last_episode.get("season", 0)
            number = last_episode.get("number", 0)
            title = last_episode.get("title", "")
            episode_label = f"S{season:02d}E{number:02d}"
            if title:
                episode_label += f": {title}"
            result += f"- **{episode_label}**\n\n"

        # Show season progress
        seasons = data.get("seasons", [])
        if seasons:
            result += "## Season Progress\n\n"
            for season in seasons:
                season_number = season["number"]
                season_aired_count = season["aired"]
                season_completed = season["completed"]
                season_percentage = (
                    (season_completed / season_aired_count * 100)
                    if season_aired_count > 0
                    else 0
                )

                season_label = (
                    "Specials" if season_number == 0 else f"Season {season_number}"
                )

                if verbose:
                    if (
                        season_completed == season_aired_count
                        and season_aired_count > 0
                    ):
                        status = "Complete (100%)"
                    else:
                        status = (
                            f"{season_completed}/{season_aired_count} "
                            f"({season_percentage:.0f}%)"
                        )

                    result += f"### {season_label}\n\n"
                    result += f"**Progress:** {status}\n\n"

                    episodes = season.get("episodes", [])
                    if episodes:
                        for episode in episodes:
                            episode_number = episode["number"]
                            episode_completed = episode["completed"]
                            last_watched = episode.get("last_watched_at")

                            status_icon = "x" if episode_completed else " "
                            episode_label = f"E{episode_number:02d}"

                            if episode_completed and last_watched:
                                watched_str = format_iso_timestamp(last_watched)
                                result += (
                                    f"- [{status_icon}] **{episode_label}** - "
                                    f"Watched: {watched_str}\n"
                                )
                            elif episode_completed:
                                result += (
                                    f"- [{status_icon}] **{episode_label}** - Watched\n"
                                )
                            else:
                                result += (
                                    f"- [{status_icon}] **{episode_label}** - "
                                    f"Not watched\n"
                                )

                    result += "\n"
                else:
                    if (
                        season_completed == season_aired_count
                        and season_aired_count > 0
                    ):
                        status = "Complete (100%)"
                    else:
                        status = (
                            f"{season_completed}/{season_aired_count} "
                            f"({season_percentage:.0f}%)"
                        )

                    result += f"- **{season_label}:** {status}\n"

        # Show hidden seasons if present
        hidden_seasons = data.get("hidden_seasons", [])
        if hidden_seasons:
            result += "\n## Hidden Seasons\n\n"
            for hidden in hidden_seasons:
                result += f"- Season {hidden['number']}\n"

        return result

    @staticmethod
    def format_playback_progress(items: list[PlaybackProgressResponse]) -> str:
        """Format playback progress items as markdown.

        Args:
            items: List of playback progress items from API

        Returns:
            Formatted markdown text with playback items
        """
        if not items:
            return (
                "# Playback Progress\n\n"
                "No paused playback items found.\n\n"
                "Items appear here when you pause a movie or episode during playback."
            )

        result = f"# Playback Progress ({len(items)} item{'s' if len(items) != 1 else ''})\n\n"

        # Group by type
        movies = [i for i in items if i["type"] == "movie"]
        episodes = [i for i in items if i["type"] == "episode"]

        if movies:
            result += "## Movies\n\n"
            for item in movies:
                movie = item.get("movie", {})
                title = movie.get("title", "Unknown")
                year = movie.get("year")
                progress = item["progress"]
                paused_at = item["paused_at"]
                playback_id = item["id"]

                title_str = f"{title} ({year})" if year else title
                paused_str = format_iso_timestamp(paused_at)

                result += f"- **{title_str}**\n"
                result += f"  - Progress: {progress:.1f}%\n"
                result += f"  - Paused: {paused_str}\n"
                result += f"  - ID: {playback_id} (use with `remove_playback_item`)\n\n"

        if episodes:
            result += "## Episodes\n\n"
            for item in episodes:
                episode = item.get("episode", {})
                show = item.get("show", {})
                show_title = show.get("title", "Unknown Show")
                season = episode.get("season", 0)
                number = episode.get("number", 0)
                ep_title = episode.get("title", "")
                progress = item["progress"]
                paused_at = item["paused_at"]
                playback_id = item["id"]

                ep_str = f"{show_title} - S{season:02d}E{number:02d}"
                if ep_title:
                    ep_str += f": {ep_title}"

                paused_str = format_iso_timestamp(paused_at)

                result += f"- **{ep_str}**\n"
                result += f"  - Progress: {progress:.1f}%\n"
                result += f"  - Paused: {paused_str}\n"
                result += f"  - ID: {playback_id} (use with `remove_playback_item`)\n\n"

        return result
