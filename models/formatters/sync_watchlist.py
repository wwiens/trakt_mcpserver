"""Sync watchlist formatting methods for the Trakt MCP server."""

from models.sync.watchlist import SyncWatchlistSummary, TraktWatchlistItem
from models.types.pagination import PaginatedResponse


class SyncWatchlistFormatters:
    """Helper class for formatting sync watchlist data for MCP responses."""

    @staticmethod
    def format_user_watchlist(
        paginated_items: PaginatedResponse[TraktWatchlistItem],
        watchlist_type: str,
        sort_by: str,
        sort_how: str,
    ) -> str:
        """Format user's watchlist with pagination information.

        Args:
            paginated_items: Paginated response with watchlist items
                and pagination metadata
            watchlist_type: Type of content (all, movies, shows, seasons, episodes)
            sort_by: Sorting field (rank, added, title, etc.)
            sort_how: Sort direction (asc, desc)

        Returns:
            Formatted markdown text with watchlist items and pagination information
        """
        items = paginated_items.data
        pagination = paginated_items.pagination

        # Determine display label and item noun based on watchlist_type
        if watchlist_type == "all":
            display_label = "Watchlist"
            item_noun = "items"
        else:
            display_label = watchlist_type
            item_noun = None  # Will be computed later based on count

        # Handle empty state
        if not items:
            result = f"# Your {display_label.title()} Watchlist\n\n"
            result += f"Your {display_label} watchlist is empty. "
            result += (
                "Use the `add_user_watchlist` tool to add items to your watchlist.\n\n"
            )

            # Show pagination info even for empty results
            result += f"📄 **Pagination Info:** {paginated_items.page_info_summary()}\n"
            return result

        # Title with sort info
        sort_desc = f" (sorted by {sort_by}, {sort_how})"
        result = f"# Your {display_label.title()} Watchlist{sort_desc}\n\n"

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

        # Handle pluralization
        count = len(items)
        if watchlist_type == "all":
            noun = item_noun  # Use "items" for "all" case
        else:
            # Existing singular/plural derivation
            noun = watchlist_type[:-1] if count == 1 else watchlist_type
        result += f"Found {count} {noun} on this page:\n\n"

        # Group by type if "all" is selected
        if watchlist_type == "all":
            items_by_type: dict[str, list[TraktWatchlistItem]] = {}
            for item in items:
                if item.type not in items_by_type:
                    items_by_type[item.type] = []
                items_by_type[item.type].append(item)

            # Display grouped by type
            for item_type in sorted(items_by_type.keys()):
                type_items = items_by_type[item_type]
                count = len(type_items)
                noun = item_type + "s" if count > 1 else item_type
                result += f"## {item_type.title()}s ({count} {noun})\n\n"
                result += SyncWatchlistFormatters._format_watchlist_items(type_items)
                result += "\n"
        else:
            # Display all items without grouping
            result += SyncWatchlistFormatters._format_watchlist_items(items)

        return result

    @staticmethod
    def _format_watchlist_items(items: list[TraktWatchlistItem]) -> str:
        """Format a list of watchlist items as markdown.

        Args:
            items: List of watchlist items to format

        Returns:
            Formatted markdown text for the items
        """
        result = ""
        for item in items:
            title = "Unknown"
            year = ""

            if item.movie:
                title = item.movie.title
                year = f" ({item.movie.year})" if item.movie.year else ""
            elif item.episode and item.show:
                season = item.episode.season
                episode = item.episode.number
                episode_title = item.episode.title
                title = f"{item.show.title} - S{season:02d}E{episode:02d}"
                if episode_title:
                    title += f": {episode_title}"
                year = f" ({item.show.year})" if item.show.year else ""
            elif item.season and item.show:
                title = f"{item.show.title} - Season {item.season.number}"
                year = f" ({item.show.year})" if item.show.year else ""
            elif item.show:
                title = item.show.title
                year = f" ({item.show.year})" if item.show.year else ""

            # Format listed date
            listed_date = (
                item.listed_at.strftime("%Y-%m-%d")
                if item.listed_at
                else "Unknown date"
            )

            # Build the line
            result += f"- **{title}{year}** (rank #{item.rank}, added {listed_date})"

            # Add notes if present (VIP feature)
            if item.notes:
                result += f"\n  - 📝 **Note:** {item.notes}"

            result += "\n"

        return result

    @staticmethod
    def format_user_watchlist_summary(
        summary: SyncWatchlistSummary, operation: str, watchlist_type: str
    ) -> str:
        """Format add/remove operation results with counts.

        Args:
            summary: Summary of the sync operation
            operation: Type of operation ("added" or "removed")
            watchlist_type: Type of content operated on

        Returns:
            Formatted markdown text with operation results and summary
        """
        result = f"# Watchlist {operation.title()} - {watchlist_type.title()}\n\n"

        # Get the counts for the specific operation
        counts = None
        if operation == "added" and summary.added:
            counts = summary.added
        elif operation == "removed" and summary.deleted:
            counts = summary.deleted

        if counts:
            total = getattr(counts, watchlist_type, 0)
            if total > 0:
                result += (
                    f"✅ Successfully {operation} **{total}** "
                    f"{watchlist_type} item(s) to/from your watchlist.\n\n"
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
                result += f"No {watchlist_type} items were {operation}.\n\n"
        else:
            result += f"No {watchlist_type} items were {operation}.\n\n"

        # Show existing items (for add operations)
        if operation == "added" and summary.existing:
            existing_count = getattr(summary.existing, watchlist_type, 0)
            if existing_count > 0:
                result += f"## Items Already in Watchlist ({existing_count})\n\n"
                result += (
                    f"**{existing_count}** {watchlist_type} item(s) were already "
                    f"in your watchlist and were not added again.\n\n"
                )

        # Show items that were not found
        if summary.not_found:
            not_found_items = getattr(summary.not_found, watchlist_type, [])
            if not_found_items:
                result += f"## Items Not Found ({len(not_found_items)})\n\n"
                result += "The following items could not be found on Trakt:\n\n"

                for item in not_found_items:
                    # Extract identifying information from the item
                    item_title = getattr(item, "title", None)
                    item_year = getattr(item, "year", None)
                    item_ids = getattr(item, "ids", None)

                    if item_title:
                        display_name = item_title
                        if item_year:
                            display_name += f" ({item_year})"
                    elif item_ids:
                        # Show IDs if no title available
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
