"""Sync ratings formatting methods for the Trakt MCP server."""

from models.sync.ratings import SyncRatingsSummary, TraktSyncRating


class SyncRatingsFormatters:
    """Helper class for formatting sync ratings data for MCP responses."""

    @staticmethod
    def format_user_ratings(
        ratings: list[TraktSyncRating],
        rating_type: str,
        rating_filter: int | None = None,
    ) -> str:
        """Format user's personal ratings by type.

        Args:
            ratings: List of user's sync ratings
            rating_type: Type of content (movies, shows, seasons, episodes)
            rating_filter: Optional specific rating filter applied

        Returns:
            Formatted markdown text with user's ratings grouped by type
        """
        # Handle empty state
        if not ratings:
            filter_text = f" with rating {rating_filter}" if rating_filter else ""
            return (
                f"# Your {rating_type.title()} Ratings{filter_text}\n\n"
                f"You haven't rated any {rating_type} yet{filter_text}. "
                f"Use the `add_user_ratings` tool to add ratings for your {rating_type}."
            )

        filter_text = f" (filtered to rating {rating_filter})" if rating_filter else ""
        result = f"# Your {rating_type.title()} Ratings{filter_text}\n\n"
        result += f"Found {len(ratings)} rated {rating_type}:\n\n"

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
            result += (
                f"## Rating {rating_score}/10 ({len(rated_items)} {rating_type})\n\n"
            )

            for rating_item in rated_items:
                title = "Unknown"
                year = ""

                if rating_item.movie:
                    title = rating_item.movie.title
                    year = (
                        f" ({rating_item.movie.year})" if rating_item.movie.year else ""
                    )
                elif rating_item.show:
                    title = rating_item.show.title
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

                # Format rating date (show just the date part)
                rating_date = (
                    rating_item.rated_at[:10]
                    if rating_item.rated_at
                    else "Unknown date"
                )

                result += f"- **{title}{year}** (rated {rating_date})\n"

            result += "\n"

        return result

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
        result = f"# Ratings {operation.title()} - {rating_type.title()}\n\n"

        # Get the counts for the specific operation
        counts = None
        if operation == "added" and summary.added:
            counts = summary.added
        elif operation == "removed" and summary.removed:
            counts = summary.removed

        if counts:
            total = getattr(counts, rating_type, 0)
            if total > 0:
                result += f"✅ Successfully {operation} **{total}** {rating_type} rating(s).\n\n"

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
                result += f"No {rating_type} ratings were {operation}.\n\n"
        else:
            result += f"No {rating_type} ratings were {operation}.\n\n"

        # Show items that were not found
        if summary.not_found:
            not_found_items = getattr(summary.not_found, rating_type, [])
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
