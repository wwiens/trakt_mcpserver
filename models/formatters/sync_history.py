"""Sync history formatting methods for the Trakt MCP server."""

from models.sync.history import HistorySummary, WatchHistoryItem
from models.types.pagination import PaginatedResponse
from utils.formatting import format_iso_timestamp


class SyncHistoryFormatters:
    """Helper class for formatting sync history data for MCP responses."""

    @staticmethod
    def format_watch_history(
        paginated_items: PaginatedResponse[WatchHistoryItem],
        query_type: str | None = None,
        item_id: str | None = None,
    ) -> str:
        """Format watch history response as markdown.

        Args:
            paginated_items: Paginated response with watch history items
                and pagination metadata
            query_type: Type filter used in query (movies, shows, etc.)
            item_id: Specific item ID that was queried

        Returns:
            Formatted markdown text with watch history and pagination information
        """
        items = paginated_items.data
        pagination = paginated_items.pagination

        if item_id:
            if not items:
                type_label = query_type.rstrip("s") if query_type else "item"
                return (
                    f"# Watch History: {item_id}\n\n"
                    f"This {type_label} has **not been watched**.\n"
                )

            watch_count = len(items)
            first_item = items[0]

            if first_item.type == "movie" and first_item.movie:
                title = first_item.movie.title
                year = first_item.movie.year
                title_str = f"{title} ({year})" if year else title
            elif first_item.type == "episode" and first_item.show:
                title = first_item.show.title
                year = first_item.show.year
                title_str = f"{title} ({year})" if year else title
            else:
                title_str = item_id

            lines: list[str] = [f"# Watch History: {title_str}", ""]
            lines.append(
                f"**Watched {watch_count} time{'s' if watch_count != 1 else ''}**"
            )
            lines.append("")

            lines.append("## Watch Events")
            lines.append("")
            for item in items:
                watched_str = format_iso_timestamp(item.watched_at)

                if item.type == "episode" and item.episode:
                    episode = item.episode
                    episode_label = f"S{episode.season:02d}E{episode.number:02d}"
                    if episode.title:
                        episode_label += f": {episode.title}"
                    lines.append(
                        f"- **{episode_label}** - {watched_str} ({item.action})"
                    )
                else:
                    lines.append(f"- {watched_str} ({item.action})")

            return "\n".join(lines)

        if not items:
            type_label = query_type if query_type else "items"
            lines = ["# Watch History", ""]
            lines.append(f"No {type_label} in watch history.")
            lines.append("")
            lines.append(
                f"📄 **Pagination Info:** {paginated_items.page_info_summary()}"
            )
            return "\n".join(lines)

        lines = [
            f"# Watch History ({len(items)} item{'s' if len(items) != 1 else ''})",
            "",
        ]

        lines.append(f"📄 **{paginated_items.page_info_summary()}**")
        lines.append("")

        navigation_hints: list[str] = []
        if pagination.has_previous_page:
            navigation_hints.append(f"Previous: page {pagination.previous_page()}")
        if pagination.has_next_page:
            navigation_hints.append(f"Next: page {pagination.next_page()}")

        if navigation_hints:
            lines.append(f"📍 **Navigation:** {' | '.join(navigation_hints)}")
            lines.append("")

        movies = [i for i in items if i.type == "movie"]
        episodes = [i for i in items if i.type == "episode"]

        if movies:
            lines.append("## Movies")
            lines.append("")
            for item in movies:
                if item.movie:
                    title = item.movie.title
                    year = item.movie.year
                    title_str = f"{title} ({year})" if year else title
                    watched_str = format_iso_timestamp(item.watched_at)

                    lines.append(f"- **{title_str}** - {watched_str}")

            lines.append("")

        if episodes:
            lines.append("## Episodes")
            lines.append("")
            for item in episodes:
                if item.episode and item.show:
                    show_title = item.show.title
                    episode = item.episode
                    episode_label = (
                        f"{show_title} - S{episode.season:02d}E{episode.number:02d}"
                    )
                    if episode.title:
                        episode_label += f": {episode.title}"

                    watched_str = format_iso_timestamp(item.watched_at)

                    lines.append(f"- **{episode_label}** - {watched_str}")

        return "\n".join(lines)

    @staticmethod
    def format_history_summary(
        summary: HistorySummary, operation: str, content_type: str
    ) -> str:
        """Format history add/remove operation results as markdown.

        Args:
            summary: Summary of the history operation
            operation: Type of operation ("added" or "removed")
            content_type: Type of content operated on

        Returns:
            Formatted markdown text with operation results
        """
        lines: list[str] = [
            f"# History {operation.title()} - {content_type.title()}",
            "",
        ]

        # Get the counts for the specific operation
        counts = None
        if operation == "added" and summary.added:
            counts = summary.added
        elif operation == "removed" and summary.deleted:
            counts = summary.deleted

        if counts:
            # Sum all non-zero counts — the API may report deletions
            # under a different type (e.g., episodes when removing a show)
            type_breakdown: list[str] = []
            total = 0
            for type_name in ("movies", "shows", "seasons", "episodes"):
                count = getattr(counts, type_name, 0)
                if count > 0:
                    total += count
                    type_breakdown.append(f"{type_name.title()}: {count}")

            if total > 0:
                preposition = "to" if operation == "added" else "from"
                if len(type_breakdown) == 1:
                    label = type_breakdown[0].split(":")[0].lower()
                    if total == 1:
                        label = label.rstrip("s")
                else:
                    label = "item" if total == 1 else "items"
                summary_msg = (
                    f"Successfully {operation} **{total}**"
                    f" {label} {preposition}"
                    " watch history."
                )
                lines.append(summary_msg)
                lines.append("")

                if len(type_breakdown) > 1:
                    lines.append("### Breakdown by Type")
                    lines.extend(f"- {breakdown}" for breakdown in type_breakdown)
                    lines.append("")
            else:
                lines.append(f"No {content_type} were {operation}.")
                lines.append("")
        else:
            lines.append(f"No {content_type} were {operation}.")
            lines.append("")

        # Show items that were not found
        if summary.not_found:
            not_found_items = getattr(summary.not_found, content_type, [])
            if not_found_items:
                lines.append(f"## Items Not Found ({len(not_found_items)})")
                lines.append("")
                lines.append("The following items could not be found on Trakt:")
                lines.append("")

                for item in not_found_items:
                    item_title = item.title
                    item_year = item.year
                    item_ids = item.ids

                    if item_title:
                        display_name = item_title
                        if item_year:
                            display_name += f" ({item_year})"
                    elif item_ids:
                        id_parts: list[str] = []
                        for id_type, id_value in item_ids.model_dump(
                            exclude_none=True
                        ).items():
                            if id_value:
                                id_parts.append(f"{id_type}: {id_value}")
                        display_name = (
                            ", ".join(id_parts) if id_parts else "Unknown item"
                        )
                    else:
                        display_name = "Unknown item"

                    lines.append(f"- {display_name}")

                lines.append("")
                lines.append("Please check the titles, years, and IDs for accuracy.")

        return "\n".join(lines)
