"""Comments formatting methods for the Trakt MCP server."""

from models.formatters.utils import format_display_time, format_pagination_header
from models.types import CommentResponse
from models.types.pagination import PaginatedResponse


class CommentsFormatters:
    """Helper class for formatting comment-related data for MCP responses."""

    @staticmethod
    def format_comments(
        data: list[CommentResponse] | PaginatedResponse[CommentResponse],
        title: str,
        show_spoilers: bool = False,
    ) -> str:
        """Format comments for MCP resource.

        Args:
            data: Either a list of all comments or a paginated response
            title: Title to use in the formatted output
            show_spoilers: Whether to show spoiler content

        Returns:
            Formatted markdown text with comments
        """
        lines: list[str] = [f"# Comments for {title}", ""]

        # Handle pagination metadata if present
        if isinstance(data, PaginatedResponse):
            lines.append(format_pagination_header(data).rstrip("\n"))
            lines.append("")
            comments = data.data
        else:
            comments = data

        if show_spoilers:
            lines.append("**Note: Showing all spoilers**")
            lines.append("")
        else:
            lines.append(
                "**Note: Spoilers are hidden. Use `show_spoilers=True` to view them.**"
            )
            lines.append("")

        if not comments:
            lines.append("No comments found.")
            return "\n".join(lines)

        for comment in comments:
            username = comment.get("user", {}).get("username", "Anonymous")
            created_at = comment.get("created_at", "Unknown date")
            comment_text = comment.get("comment", "")
            spoiler = comment.get("spoiler", False)
            review = comment.get("review", False)
            replies = comment.get("replies", 0)
            likes = comment.get("likes", 0)
            comment_id = comment.get("id", "")

            created_time = format_display_time(created_at)

            comment_type = ""
            if review:
                comment_type = " [REVIEW]"
            if spoiler:
                comment_type += " [SPOILER]"

            lines.append(f"### {username}{comment_type} - {created_time}")

            if (spoiler or "[spoiler]" in comment_text) and not show_spoilers:
                lines.append("**⚠️ SPOILER WARNING ⚠️**")
                lines.append("")
                spoiler_msg = (
                    "*This comment contains spoilers."
                    " Use `show_spoilers=True` to view it.*"
                )
                lines.append(spoiler_msg)
                lines.append("")
            else:
                if show_spoilers:
                    comment_text = comment_text.replace("[spoiler]", "")
                    comment_text = comment_text.replace("[/spoiler]", "")

                lines.append(f"{comment_text}")
                lines.append("")

            lines.append(f"*Likes: {likes} | Replies: {replies} | ID: {comment_id}*")
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_comment(
        comment: CommentResponse,
        with_replies: bool = False,
        replies: list[CommentResponse]
        | PaginatedResponse[CommentResponse]
        | None = None,
        show_spoilers: bool = False,
    ) -> str:
        """Format a single comment with optional replies.

        Args:
            comment: The comment to format
            with_replies: Whether to include replies in the output
            replies: Either a list of all replies or a paginated response
            show_spoilers: Whether to show spoiler content

        Returns:
            Formatted markdown text with the comment and optional replies
        """
        username = comment.get("user", {}).get("username", "Anonymous")
        created_at = comment.get("created_at", "Unknown date")
        comment_text = comment.get("comment", "")
        spoiler = comment.get("spoiler", False)
        review = comment.get("review", False)
        replies_count = comment.get("replies", 0)
        likes = comment.get("likes", 0)
        comment_id = comment.get("id", "")

        created_time = format_display_time(created_at)

        comment_type = ""
        if review:
            comment_type = " [REVIEW]"
        if spoiler:
            comment_type += " [SPOILER]"

        lines: list[str] = [f"# Comment by {username}{comment_type}", ""]

        if show_spoilers:
            lines.append("**Note: Showing all spoilers**")
            lines.append("")
        else:
            lines.append(
                "**Note: Spoilers are hidden. Use `show_spoilers=True` to view them.**"
            )
            lines.append("")

        lines.append(f"**Posted:** {created_time}")
        lines.append("")

        if (spoiler or "[spoiler]" in comment_text) and not show_spoilers:
            lines.append("**⚠️ SPOILER WARNING ⚠️**")
            lines.append("")
            lines.append(
                "*This comment contains spoilers. Use `show_spoilers=True` to view it.*"
            )
            lines.append("")
        else:
            if show_spoilers:
                comment_text = comment_text.replace("[spoiler]", "")
                comment_text = comment_text.replace("[/spoiler]", "")

            lines.append(f"{comment_text}")
            lines.append("")

        lines.append(f"*Likes: {likes} | Replies: {replies_count} | ID: {comment_id}*")
        lines.append("")

        if with_replies and replies:
            lines.append("## Replies")
            lines.append("")

            # Handle pagination metadata if present
            if isinstance(replies, PaginatedResponse):
                lines.append(format_pagination_header(replies).rstrip("\n"))
                lines.append("")
                replies_list = replies.data
            else:
                replies_list = replies

            for reply in replies_list:
                reply_username = reply.get("user", {}).get("username", "Anonymous")
                reply_created_at = reply.get("created_at", "Unknown date")
                reply_text = reply.get("comment", "")
                reply_spoiler = reply.get("spoiler", False)
                reply_id = reply.get("id", "")

                reply_time = format_display_time(reply_created_at)

                reply_type = ""
                if reply.get("review", False):
                    reply_type = " [REVIEW]"
                if reply_spoiler:
                    reply_type += " [SPOILER]"

                lines.append(f"### {reply_username}{reply_type} - {reply_time}")

                if (reply_spoiler or "[spoiler]" in reply_text) and not show_spoilers:
                    lines.append("**⚠️ SPOILER WARNING ⚠️**")
                    lines.append("")
                    spoiler_msg = (
                        "*This reply contains spoilers."
                        " Use `show_spoilers=True`"
                        " to view it.*"
                    )
                    lines.append(spoiler_msg)
                    lines.append("")
                else:
                    if show_spoilers:
                        reply_text = reply_text.replace("[spoiler]", "")
                        reply_text = reply_text.replace("[/spoiler]", "")

                    lines.append(f"{reply_text}")
                    lines.append("")

                lines.append(f"*ID: {reply_id}*")
                lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)
