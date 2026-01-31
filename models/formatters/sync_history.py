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

        # If querying a specific item, show targeted response
        if item_id:
            if not items:
                type_label = query_type.rstrip("s") if query_type else "item"
                return (
                    f"# Watch History: {item_id}\n\n"
                    f"This {type_label} has **not been watched**.\n"
                )

            # Count unique watches
            watch_count = len(items)
            first_item = items[0]

            # Get title from the item
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

            result = f"# Watch History: {title_str}\n\n"
            result += (
                f"**Watched {watch_count} time{'s' if watch_count != 1 else ''}**\n\n"
            )

            result += "## Watch Events\n\n"
            for item in items:
                watched_str = format_iso_timestamp(item.watched_at)

                if item.type == "episode" and item.episode:
                    ep = item.episode
                    ep_str = f"S{ep.season:02d}E{ep.number:02d}"
                    if ep.title:
                        ep_str += f": {ep.title}"
                    result += f"- **{ep_str}** - {watched_str} ({item.action})\n"
                else:
                    result += f"- {watched_str} ({item.action})\n"

            return result

        # General history listing
        if not items:
            type_label = query_type if query_type else "items"
            result = f"# Watch History\n\nNo {type_label} in watch history.\n\n"
            result += f"📄 **Pagination Info:** {paginated_items.page_info_summary()}\n"
            return result

        result = (
            f"# Watch History ({len(items)} item{'s' if len(items) != 1 else ''})\n\n"
        )

        # Show pagination summary at the top
        result += f"📄 **{paginated_items.page_info_summary()}**\n\n"

        # Show page navigation hints
        navigation_hints: list[str] = []
        if pagination.has_previous_page:
            navigation_hints.append(f"Previous: page {pagination.previous_page()}")
        if pagination.has_next_page:
            navigation_hints.append(f"Next: page {pagination.next_page()}")

        if navigation_hints:
            result += f"📍 **Navigation:** {' | '.join(navigation_hints)}\n\n"

        # Group by type
        movies = [i for i in items if i.type == "movie"]
        episodes = [i for i in items if i.type == "episode"]

        if movies:
            result += "## Movies\n\n"
            for item in movies:
                if item.movie:
                    title = item.movie.title
                    year = item.movie.year
                    title_str = f"{title} ({year})" if year else title
                    watched_str = format_iso_timestamp(item.watched_at)

                    result += f"- **{title_str}** - {watched_str}\n"

            result += "\n"

        if episodes:
            result += "## Episodes\n\n"
            for item in episodes:
                if item.episode and item.show:
                    show_title = item.show.title
                    ep = item.episode
                    ep_str = f"{show_title} - S{ep.season:02d}E{ep.number:02d}"
                    if ep.title:
                        ep_str += f": {ep.title}"

                    watched_str = format_iso_timestamp(item.watched_at)

                    result += f"- **{ep_str}** - {watched_str}\n"

        return result

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
        result = f"# History {operation.title()} - {content_type.title()}\n\n"

        # Get the counts for the specific operation
        counts = None
        if operation == "added" and summary.added:
            counts = summary.added
        elif operation == "removed" and summary.deleted:
            counts = summary.deleted

        if counts:
            total = getattr(counts, content_type, 0)
            if total > 0:
                preposition = "to" if operation == "added" else "from"
                result += (
                    f"Successfully {operation} **{total}** "
                    f"{content_type} {preposition} watch history.\n\n"
                )

                # Show breakdown by type if multiple types were processed
                type_breakdown: list[str] = []
                if counts.movies > 0:
                    type_breakdown.append(f"Movies: {counts.movies}")
                if counts.shows > 0:
                    type_breakdown.append(f"Shows: {counts.shows}")
                if counts.seasons > 0:
                    type_breakdown.append(f"Seasons: {counts.seasons}")
                if counts.episodes > 0:
                    type_breakdown.append(f"Episodes: {counts.episodes}")

                if len(type_breakdown) > 1:
                    result += "### Breakdown by Type\n"
                    for breakdown in type_breakdown:
                        result += f"- {breakdown}\n"
                    result += "\n"
            else:
                result += f"No {content_type} were {operation}.\n\n"
        else:
            result += f"No {content_type} were {operation}.\n\n"

        # Show items that were not found
        if summary.not_found:
            not_found_items = getattr(summary.not_found, content_type, [])
            if not_found_items:
                result += f"## Items Not Found ({len(not_found_items)})\n\n"
                result += "The following items could not be found on Trakt:\n\n"

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
                        for id_type, id_value in item_ids.items():
                            if id_value:
                                id_parts.append(f"{id_type}: {id_value}")
                        display_name = (
                            ", ".join(id_parts) if id_parts else "Unknown item"
                        )
                    else:
                        display_name = "Unknown item"

                    result += f"- {display_name}\n"

                result += "\nPlease check the titles, years, and IDs for accuracy.\n"

        return result
