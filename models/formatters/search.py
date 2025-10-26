"""Search formatting methods for the Trakt MCP server."""

from models.types import SearchResult
from models.types.pagination import PaginatedResponse


class SearchFormatters:
    """Helper class for formatting search-related data for MCP responses."""

    @staticmethod
    def format_show_search_results(
        results: list[SearchResult] | PaginatedResponse[SearchResult],
    ) -> str:
        """Format show search results from Trakt API.

        Args:
            results: The search results data (list or paginated response)

        Returns:
            Formatted search results message
        """
        # Handle pagination
        if isinstance(results, PaginatedResponse):
            # Paginated response - format with pagination info
            message = "# Show Search Results\n\n"
            message += f"📄 **{results.page_info_summary()}**\n\n"

            # Add navigation hints
            if results.pagination.has_previous_page or results.pagination.has_next_page:
                message += "📍 **Navigation:** "
                if results.pagination.has_previous_page:
                    message += f"Previous: page {results.pagination.previous_page} | "
                if results.pagination.has_next_page:
                    message += f"Next: page {results.pagination.next_page}"
                message += "\n\n"

            items = results.data
            if not items:
                return (
                    message
                    + "No shows found on this page. Try a different page or search query."
                )
        else:
            # Non-paginated response - all results
            items = results
            if not items:
                return "# Show Search Results\n\nNo shows found matching your query."

            message = "# Show Search Results\n\n"
            message += "Here are the shows matching your search query:\n\n"

        # Format items
        for index, item in enumerate(items, 1):
            show = item.get("show", {})

            # Extract show details
            title = show.get("title", "Unknown show")
            year = show.get("year", "")
            year_str = f" ({year})" if year else ""

            # Extract IDs
            ids = show.get("ids", {})
            trakt_id = ids.get("trakt", "unknown")

            # Format the result entry with the Trakt ID included for easy reference
            message += f"**{index}. {title}{year_str}** (ID: {trakt_id})\n"

            # Add overview if available
            if overview := show.get("overview"):
                # Truncate long overviews
                if len(overview) > 200:
                    overview = overview[:197] + "..."
                message += f"  {overview}\n"

            # Add a note about using this ID for check-ins
            message += f"  *Use this ID for check-ins: `{trakt_id}`*\n\n"

        # Add a tip for using the search results
        message += "\nTo check in to a show, use the `checkin_to_show` tool with the show ID, season number, and episode number."

        return message

    @staticmethod
    def format_movie_search_results(
        results: list[SearchResult] | PaginatedResponse[SearchResult],
    ) -> str:
        """Format movie search results from Trakt API.

        Args:
            results: The search results data (list or paginated response)

        Returns:
            Formatted search results message
        """
        # Handle pagination
        if isinstance(results, PaginatedResponse):
            # Paginated response - format with pagination info
            message = "# Movie Search Results\n\n"
            message += f"📄 **{results.page_info_summary()}**\n\n"

            # Add navigation hints
            if results.pagination.has_previous_page or results.pagination.has_next_page:
                message += "📍 **Navigation:** "
                if results.pagination.has_previous_page:
                    message += f"Previous: page {results.pagination.previous_page} | "
                if results.pagination.has_next_page:
                    message += f"Next: page {results.pagination.next_page}"
                message += "\n\n"

            items = results.data
            if not items:
                return (
                    message
                    + "No movies found on this page. Try a different page or search query."
                )
        else:
            # Non-paginated response - all results
            items = results
            if not items:
                return "# Movie Search Results\n\nNo movies found matching your query."

            message = "# Movie Search Results\n\n"
            message += "Here are the movies matching your search query:\n\n"

        # Format items
        for index, item in enumerate(items, 1):
            movie = item.get("movie", {})

            title = movie.get("title", "Unknown movie")
            year = movie.get("year", "")
            year_str = f" ({year})" if year else ""

            ids = movie.get("ids", {})
            trakt_id = ids.get("trakt", "unknown")

            message += f"**{index}. {title}{year_str}** (ID: {trakt_id})\n"

            if overview := movie.get("overview"):
                if len(overview) > 200:
                    overview = overview[:197] + "..."
                message += f"  {overview}\n"

            message += f"  *Use this ID for comments: `{trakt_id}`*\n\n"

        message += "\nTo view comments for a movie, use the `fetch_movie_comments` tool with the movie ID."

        return message
