"""Markdown formatting for personal list metadata and mutation summaries."""

from models.formatters.sync_watchlist import SyncWatchlistFormatters
from models.sync.watchlist import SyncWatchlistSummary
from models.user.lists import UserList


class UserListFormatters:
    """Format personal lists without fetching their contents."""

    @staticmethod
    def format_lists(lists: list[UserList]) -> str:
        """Display list identifiers, visibility, item counts and descriptions."""
        lines = ["# Your Personal Lists", ""]
        if not lists:
            lines.append("You have no personal lists.")
        for user_list in lists:
            lines.extend(
                [
                    f"## {user_list.name}",
                    f"- Trakt ID: {user_list.ids.trakt}",
                    f"- Slug: {user_list.ids.slug}",
                    f"- Privacy: {user_list.privacy}",
                    f"- Items: {user_list.item_count}",
                    f"- Description: {user_list.description or ''}",
                    "",
                ]
            )
        return "\n".join(lines)

    @staticmethod
    def format_items(
        summary: SyncWatchlistSummary, operation: str, item_type: str, list_id: str
    ) -> str:
        """Use the shared collection summary, retaining not-found identifiers."""
        formatted = SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, operation, item_type, collection_label="List"
        )
        return f"List: {list_id}\n\n{formatted}"
