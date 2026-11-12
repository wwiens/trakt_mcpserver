"""Markdown formatting for personal list metadata, contents and summaries."""

from models.formatters.sync_watchlist import SyncWatchlistFormatters
from models.formatters.utils import format_pagination_header, format_title_year
from models.sync.watchlist import SyncWatchlistSummary
from models.types.pagination import PaginatedResponse
from models.user.lists import UserList, UserListItem


class UserListFormatters:
    """Format personal list metadata, contents and mutation results."""

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

    @staticmethod
    def format_list_items(
        data: list[UserListItem] | PaginatedResponse[UserListItem], list_id: str
    ) -> str:
        """Display item identity, notes and page navigation when available."""
        lines = [f"# Your Personal List Items: {list_id}", ""]
        if isinstance(data, PaginatedResponse):
            lines.append(format_pagination_header(data))
            items = data.data
        else:
            items = data
        if not items:
            lines.append("No items found in this list.")
        for item in items:
            title = "Unavailable item"
            year: int | None = None
            ids = None
            if item.type == "movie" and item.movie:
                title, year, ids = item.movie.title, item.movie.year, item.movie.ids
            elif item.type == "show" and item.show:
                title, year, ids = item.show.title, item.show.year, item.show.ids
            elif item.type == "season" and item.season:
                title = f"Season {item.season.number}"
                ids = item.season.ids
                if item.show:
                    title = f"{item.show.title} - {title}"
                    year = item.show.year
            elif item.type == "episode" and item.episode:
                title = f"S{item.episode.season:02d}E{item.episode.number:02d}"
                if item.episode.title:
                    title += f": {item.episode.title}"
                ids = item.episode.ids
                if item.show:
                    title = f"{item.show.title} - {title}"
                    year = item.show.year
            elif item.type == "person" and item.person:
                title, ids = item.person.name, item.person.ids
            trakt_id = ids.trakt if ids is not None else None
            lines.append(
                f"- #{item.rank} **{format_title_year(title, year)}**"
                + f" | Type: {item.type} | Trakt ID: {trakt_id or 'N/A'}"
                + f" | List item ID: {item.id}"
            )
            if item.notes:
                lines.append(f"  - Notes: {item.notes}")
        return "\n".join(lines)
