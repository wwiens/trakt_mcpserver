"""Sync ratings formatting methods for the Trakt MCP server."""

from models.sync.ratings import SyncRatingsSummary, TraktSyncRating
from models.types.pagination import PaginatedResponse


class SyncRatingsFormatters:
    """Helper class for formatting sync ratings data for MCP responses."""

    @staticmethod
    def format_user_ratings(
        paginated_ratings: PaginatedResponse[TraktSyncRating],
        rating_type: str,
        rating_filter: int | None = None,
    ) -> str:
        """Format user's personal ratings with pagination information.

        Args:
            paginated_ratings: Paginated response with ratings data
                and pagination metadata
            rating_type: Type of content (movies, shows, seasons, episodes)
            rating_filter: Optional specific rating filter applied

        Returns:
            Formatted markdown text with user's ratings and pagination information
        """
        ratings = paginated_ratings.data
        pagination = paginated_ratings.pagination

        # Handle empty state
        if not ratings:
            lines: list[str] = [f"# Your {rating_type.title()} Ratings", ""]
            if rating_filter:
                empty_msg = (
                    f"You haven't rated any {rating_type}"
                    f" with rating {rating_filter} yet."
                    f" Use the `add_user_ratings` tool"
                    f" to add ratings for your {rating_type}."
                )
                lines.append(empty_msg)
            else:
                empty_msg = (
                    f"You haven't rated any {rating_type}"
                    " yet. Use the `add_user_ratings` tool"
                    f" to add ratings for your {rating_type}."
                )
                lines.append(empty_msg)
            lines.append("")

            # Show pagination info even for empty results
            lines.append(
                f"📄 **Pagination Info:** {paginated_ratings.page_info_summary()}"
            )
            return "\n".join(lines)

        filter_text = f" (filtered to rating {rating_filter})" if rating_filter else ""
        lines = [f"# Your {rating_type.title()} Ratings{filter_text}", ""]

        # Show pagination summary at the top
        lines.append(f"📄 **{paginated_ratings.page_info_summary()}**")
        lines.append("")

        # Show page navigation hints
        navigation_hints: list[str] = []
        if pagination.has_previous_page:
            navigation_hints.append(f"Previous: page {pagination.previous_page()}")
        if pagination.has_next_page:
            navigation_hints.append(f"Next: page {pagination.next_page()}")

        if navigation_hints:
            lines.append(f"📍 **Navigation:** {' | '.join(navigation_hints)}")
            lines.append("")

        # Handle pluralization for "Found X rated Y" line
        count = len(ratings)
        noun = rating_type[:-1] if count == 1 else rating_type
        lines.append(f"Found {count} rated {noun} on this page:")
        lines.append("")

        # Group ratings by rating value for better organization
        ratings_by_score: dict[int, list[TraktSyncRating]] = {}
        for rating_item in ratings:
            score = rating_item.rating
            if score not in ratings_by_score:
                ratings_by_score[score] = []
            ratings_by_score[score].append(rating_item)

        # Display ratings grouped by score (highest first)
        for rating_score in sorted(ratings_by_score.keys(), reverse=True):
            rated_items = ratings_by_score[rating_score]
            # Handle pluralization for rating section headings
            count = len(rated_items)
            noun = rating_type[:-1] if count == 1 else rating_type
            lines.append(f"## Rating {rating_score}/10 ({count} {noun})")
            lines.append("")

            for rating_item in rated_items:
                title = "Unknown"
                year = ""

                if rating_item.movie:
                    title = rating_item.movie.title
                    year = (
                        f" ({rating_item.movie.year})" if rating_item.movie.year else ""
                    )
                elif rating_item.episode and rating_item.show:
                    season = rating_item.episode.season
                    episode = rating_item.episode.number
                    episode_title = rating_item.episode.title
                    title = f"{rating_item.show.title} - S{season:02d}E{episode:02d}"
                    if episode_title:
                        title += f": {episode_title}"
                    year = (
                        f" ({rating_item.show.year})" if rating_item.show.year else ""
                    )
                elif rating_item.season and rating_item.show:
                    title = (
                        f"{rating_item.show.title} - Season {rating_item.season.number}"
                    )
                    year = (
                        f" ({rating_item.show.year})" if rating_item.show.year else ""
                    )
                elif rating_item.show:
                    title = rating_item.show.title
                    year = (
                        f" ({rating_item.show.year})" if rating_item.show.year else ""
                    )

                # Format rating date (show just the date part)
                rating_date = (
                    rating_item.rated_at.strftime("%Y-%m-%d")
                    if rating_item.rated_at
                    else "Unknown date"
                )

                lines.append(f"- **{title}{year}** (rated {rating_date})")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_user_ratings_summary(
        summary: SyncRatingsSummary, operation: str, rating_type: str
    ) -> str:
        """Format add/remove operation results with counts.

        Args:
            summary: Summary of the sync operation
            operation: Type of operation ("added" or "removed")
            rating_type: Type of content operated on

        Returns:
            Formatted markdown text with operation results and summary
        """
        lines: list[str] = [
            f"# Ratings {operation.title()} - {rating_type.title()}",
            "",
        ]

        # Get the counts for the specific operation
        counts = None
        if operation == "added" and summary.added:
            counts = summary.added
        elif operation == "removed" and summary.deleted:
            counts = summary.deleted

        if counts:
            total = getattr(counts, rating_type, 0)
            if total > 0:
                lines.append(
                    f"✅ Successfully {operation} **{total}** {rating_type} rating(s)."
                )
                lines.append("")

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
                    lines.append("### Breakdown by Type")
                    lines.extend(f"- {breakdown}" for breakdown in type_breakdown)
                    lines.append("")
            else:
                lines.append(f"No {rating_type} ratings were {operation}.")
                lines.append("")
        else:
            lines.append(f"No {rating_type} ratings were {operation}.")
            lines.append("")

        # Show items that were not found
        if summary.not_found:
            not_found_items = getattr(summary.not_found, rating_type, [])
            if not_found_items:
                lines.append(f"## Items Not Found ({len(not_found_items)})")
                lines.append("")
                lines.append("The following items could not be found on Trakt:")
                lines.append("")

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
