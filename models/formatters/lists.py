"""List formatting methods for the Trakt MCP server."""

from models.formatters.utils import (
    format_list_items_media,
    format_list_summary,
)
from models.types import ListMediaItemResponse, TrendingListResponse
from models.types.pagination import PaginatedResponse


class ListsFormatters:
    """Helper class for formatting list-related data for MCP responses."""

    @staticmethod
    def format_list_items(items: list[ListMediaItemResponse], context: str) -> str:
        """Format the items contained in a user's list."""
        return format_list_items_media(items, context)

    @staticmethod
    def format_trending_lists(
        lists: list[TrendingListResponse] | PaginatedResponse[TrendingListResponse],
    ) -> str:
        """Format trending lists data for MCP resource."""
        return format_list_summary(lists, heading="Trending Lists on Trakt")

    @staticmethod
    def format_popular_lists(
        lists: list[TrendingListResponse] | PaginatedResponse[TrendingListResponse],
    ) -> str:
        """Format popular lists data for MCP resource."""
        return format_list_summary(lists, heading="Popular Lists on Trakt")
