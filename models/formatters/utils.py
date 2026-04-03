"""Shared formatting utilities for Trakt MCP server."""

from collections.abc import Callable, Mapping, Sequence
from typing import Any, Final, TypeVar

from models.types.pagination import PaginatedResponse
from utils.formatting import DISPLAY_DATETIME_FORMAT, format_iso_timestamp

T = TypeVar("T")

MAX_OVERVIEW_LENGTH: Final[int] = 200


def format_pagination_header(results: PaginatedResponse[T]) -> str:
    """Format pagination metadata and navigation hints.

    Args:
        results: Paginated response with metadata

    Returns:
        Formatted markdown string with page info and navigation
    """
    message = f"📄 **{results.page_info_summary()}**\n\n"

    # Add navigation hints if applicable
    if results.pagination.has_previous_page or results.pagination.has_next_page:
        nav_parts: list[str] = []
        if results.pagination.has_previous_page:
            nav_parts.append(f"Previous: page {results.pagination.previous_page()}")
        if results.pagination.has_next_page:
            nav_parts.append(f"Next: page {results.pagination.next_page()}")
        message += f"📍 **Navigation:** {' | '.join(nav_parts)}\n\n"

    return message


def format_display_time(timestamp: str) -> str:
    """Format ISO 8601 timestamp for display.

    Handles Trakt API timestamp format (ISO 8601 with 'Z' timezone).

    Args:
        timestamp: ISO 8601 timestamp string (e.g., "2023-01-01T12:34:56.789Z")

    Returns:
        Formatted timestamp string (e.g., "2023-01-01 12:34:56")
        Falls back to original string if parsing fails
    """
    return format_iso_timestamp(timestamp, fmt=DISPLAY_DATETIME_FORMAT)


def format_title_year(title: str, year: str | int | None) -> str:
    """Format a title with optional year suffix.

    Args:
        title: Media title
        year: Year value (int, str, or None/empty)

    Returns:
        Formatted string like ``"Title (2024)"`` or just ``"Title"``
    """
    year_str = f" ({year})" if year else ""
    return f"{title}{year_str}"


def format_rating_distribution(distribution: dict[str, int], votes: int) -> str:
    """Format a rating distribution as a markdown table.

    Args:
        distribution: Mapping of rating values (as strings) to vote counts
        votes: Total number of votes (used for percentage calculation)

    Returns:
        Formatted markdown table string
    """
    lines: list[str] = ["## Rating Distribution"]
    lines.append("")
    lines.append("| Rating | Votes | Percentage |")
    lines.append("|--------|-------|------------|")

    for rating in range(10, 0, -1):
        rating_str = str(rating)
        count = distribution.get(rating_str, 0)
        percentage = (count / votes * 100) if votes > 0 else 0
        lines.append(f"| {rating}/10 | {count} | {percentage:.1f}% |")

    return "\n".join(lines)


def format_list_items(
    lists: Sequence[Mapping[str, Any]],
    context: str,
    item_type: str,
) -> str:
    """Format lists containing a specific item.

    Args:
        lists: List of list data from Trakt API
        context: Display context for the heading (e.g., "Breaking Bad - S01E01")
        item_type: Item type for the empty message (e.g., "episode", "season", "person")

    Returns:
        Formatted markdown text with lists
    """
    lines: list[str] = [f"# Lists Containing {context}"]
    lines.append("")

    if not lists:
        return "\n".join(lines) + f"No lists found containing this {item_type}."

    lines.append(f"**{len(lists)} list(s)**")
    lines.append("")

    for list_item in lists:
        name = list_item.get("name", "Unknown List")
        item_count = list_item.get("item_count", 0)
        likes = list_item.get("likes", 0)
        user = list_item.get("user", {})
        username = user.get("username", "Unknown")

        lines.append(f"- **{name}** by {username} ({item_count} items, {likes} likes)")

        if description := list_item.get("description"):
            if len(description) > MAX_OVERVIEW_LENGTH:
                description = description[: MAX_OVERVIEW_LENGTH - 3] + "..."
            lines.append(f"  {description}")

    return "\n".join(lines)


def format_media_list(
    data: list[Any] | PaginatedResponse[Any],
    heading: str,
    media_key: str | None,
    format_metric: Callable[[dict[str, Any]], str] | None = None,
) -> str:
    """Format a paginated or plain list of media items with optional metrics.

    Handles trending, popular, favorited, played, watched, and anticipated lists
    for both movies and shows.

    Args:
        data: Either a list of items or a paginated response
        heading: Section heading (e.g., "Trending Movies on Trakt")
        media_key: Key to extract media object from wrapper (e.g., "movie", "show"),
            or None if the items ARE the media objects directly (e.g., popular lists)
        format_metric: Optional callable that takes a wrapper item and returns
            a metric string (e.g., "42 watchers"). None for no metric suffix.

    Returns:
        Formatted markdown text
    """
    lines: list[str] = [f"# {heading}"]
    lines.append("")

    if isinstance(data, PaginatedResponse):
        lines.append(format_pagination_header(data).rstrip("\n"))
        lines.append("")
        items: list[Any] = data.data
    else:
        items = data

    for item in items:
        if media_key is not None:
            media = item.get(media_key, {})
            if not media:
                continue
        else:
            media = item

        title = media.get("title", "Unknown")
        year = media.get("year", "")
        title_str = format_title_year(title, year)

        metric_str = ""
        if format_metric is not None:
            metric_str = f" - {format_metric(item)}"

        lines.append(f"- **{title_str}**{metric_str}")

        if overview := media.get("overview"):
            if len(overview) > MAX_OVERVIEW_LENGTH:
                overview = overview[: MAX_OVERVIEW_LENGTH - 3] + "..."
            lines.append(f"  {overview}")

        lines.append("")

    return "\n".join(lines)
