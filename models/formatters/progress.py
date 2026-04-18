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
        aired = data.aired
        completed = data.completed
        percentage = (completed / aired * 100) if aired > 0 else 0

        lines: list[str] = [f"# Show Progress: {show_id}"]
        lines.append("")
        lines.append("## Overall Progress")
        lines.append("")
        lines.append(f"- **Watched:** {completed}/{aired} episodes ({percentage:.1f}%)")

        last_watched = data.last_watched_at
        if last_watched:
            lines.append(f"- **Last Watched:** {format_iso_timestamp(last_watched)}")

        reset_at = data.reset_at
        if reset_at:
            lines.append(f"- **Progress Reset At:** {format_iso_timestamp(reset_at)}")

        lines.append("")

        next_episode = data.next_episode
        if next_episode:
            lines.append("## Up Next")
            lines.append("")
            season = next_episode.season
            number = next_episode.number
            title = next_episode.title or ""
            episode_label = f"S{season:02d}E{number:02d}"
            if title:
                episode_label += f": {title}"
            lines.append(f"- **{episode_label}**")
            lines.append("")

        last_episode = data.last_episode
        if last_episode:
            lines.append("## Last Watched")
            lines.append("")
            season = last_episode.season
            number = last_episode.number
            title = last_episode.title or ""
            episode_label = f"S{season:02d}E{number:02d}"
            if title:
                episode_label += f": {title}"
            lines.append(f"- **{episode_label}**")
            lines.append("")

        # Show season progress
        seasons = data.seasons
        if seasons:
            lines.append("## Season Progress")
            lines.append("")
            for season in seasons:
                season_number = season.number
                season_aired_count = season.aired
                season_completed = season.completed
                season_percentage = (
                    (season_completed / season_aired_count * 100)
                    if season_aired_count > 0
                    else 0
                )

                season_label = (
                    "Specials" if season_number == 0 else f"Season {season_number}"
                )

                if season_completed == season_aired_count and season_aired_count > 0:
                    status = "Complete (100%)"
                else:
                    status = (
                        f"{season_completed}/{season_aired_count} "
                        f"({season_percentage:.0f}%)"
                    )

                if verbose:
                    lines.append(f"### {season_label}")
                    lines.append("")
                    lines.append(f"**Progress:** {status}")
                    lines.append("")

                    episodes = season.episodes
                    if episodes:
                        for episode in episodes:
                            episode_number = episode.number
                            episode_completed = episode.completed
                            last_watched = episode.last_watched_at

                            status_icon = "x" if episode_completed else " "
                            episode_label = f"E{episode_number:02d}"

                            if episode_completed and last_watched:
                                watched_str = format_iso_timestamp(last_watched)
                                ep_line = (
                                    f"- [{status_icon}] **{episode_label}**"
                                    f" - Watched: {watched_str}"
                                )
                                lines.append(ep_line)
                            elif episode_completed:
                                lines.append(
                                    f"- [{status_icon}] **{episode_label}** - Watched"
                                )
                            else:
                                ep_line = (
                                    f"- [{status_icon}] **{episode_label}**"
                                    " - Not watched"
                                )
                                lines.append(ep_line)

                    lines.append("")
                else:
                    lines.append(f"- **{season_label}:** {status}")

        # Show hidden seasons if present
        hidden_seasons = data.hidden_seasons
        if hidden_seasons:
            lines.append("")
            lines.append("## Hidden Seasons")
            lines.append("")
            lines.extend(f"- Season {hidden.number}" for hidden in hidden_seasons)

        return "\n".join(lines)

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

        lines: list[str] = [
            f"# Playback Progress ({len(items)} item{'s' if len(items) != 1 else ''})"
        ]
        lines.append("")

        # Group by type
        movies = [i for i in items if i.type == "movie"]
        episodes = [i for i in items if i.type == "episode"]

        if movies:
            lines.append("## Movies")
            lines.append("")
            for item in movies:
                movie = item.movie
                title = movie.title if movie else "Unknown"
                year = movie.year if movie else None
                progress = item.progress
                paused_at = item.paused_at
                playback_id = item.id

                title_str = f"{title} ({year})" if year else title
                paused_str = format_iso_timestamp(paused_at)

                lines.append(f"- **{title_str}**")
                lines.append(f"  - Progress: {progress:.1f}%")
                lines.append(f"  - Paused: {paused_str}")
                lines.append(f"  - ID: {playback_id} (use with `remove_playback_item`)")
                lines.append("")

        if episodes:
            lines.append("## Episodes")
            lines.append("")
            for item in episodes:
                episode = item.episode
                show = item.show
                show_title = show.title if show else "Unknown Show"
                season = episode.season if episode else 0
                number = episode.number if episode else 0
                ep_title = episode.title if episode else ""
                progress = item.progress
                paused_at = item.paused_at
                playback_id = item.id

                ep_str = f"{show_title} - S{season:02d}E{number:02d}"
                if ep_title:
                    ep_str += f": {ep_title}"

                paused_str = format_iso_timestamp(paused_at)

                lines.append(f"- **{ep_str}**")
                lines.append(f"  - Progress: {progress:.1f}%")
                lines.append(f"  - Paused: {paused_str}")
                lines.append(f"  - ID: {playback_id} (use with `remove_playback_item`)")
                lines.append("")

        return "\n".join(lines)
