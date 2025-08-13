"""Comments formatting methods for the Trakt MCP server."""

from models.types import CommentResponse


class CommentsFormatters:
    """Helper class for formatting comment-related data for MCP responses."""

    @staticmethod
    def format_comments(
        comments: list[CommentResponse], title: str, show_spoilers: bool = False
    ) -> str:
        """Format comments for MCP resource."""
        result = f"# Comments for {title}\n\n"

        if show_spoilers:
            result += "**Note: Showing all spoilers**\n\n"
        else:
            result += "**Note: Spoilers are hidden. Use `show_spoilers=True` to view them.**\n\n"

        if not comments:
            return result + "No comments found."

        for comment in comments:
            username = comment.get("user", {}).get("username", "Anonymous")
            created_at = comment.get("created_at", "Unknown date")
            comment_text = comment.get("comment", "")
            spoiler = comment.get("spoiler", False)
            review = comment.get("review", False)
            replies = comment.get("replies", 0)
            likes = comment.get("likes", 0)
            comment_id = comment.get("id", "")

            try:
                created_time = (
                    created_at.replace("Z", "").split(".")[0].replace("T", " ")
                )
            except Exception:
                created_time = created_at

            comment_type = ""
            if review:
                comment_type = " [REVIEW]"
            if spoiler:
                comment_type += " [SPOILER]"

            result += f"### {username}{comment_type} - {created_time}\n"

            if (spoiler or "[spoiler]" in comment_text) and not show_spoilers:
                result += "**⚠️ SPOILER WARNING ⚠️**\n\n"
                result += "*This comment contains spoilers. Use `show_spoilers=True` to view it.*\n\n"
            else:
                if show_spoilers:
                    comment_text = comment_text.replace("[spoiler]", "")
                    comment_text = comment_text.replace("[/spoiler]", "")

                result += f"{comment_text}\n\n"

            result += f"*Likes: {likes} | Replies: {replies} | ID: {comment_id}*\n\n"
            result += "---\n\n"

        return result

    @staticmethod
    def format_comment(
        comment: CommentResponse,
        with_replies: bool = False,
        replies: list[CommentResponse] | None = None,
        show_spoilers: bool = False,
    ) -> str:
        """Format a single comment with optional replies."""
        username = comment.get("user", {}).get("username", "Anonymous")
        created_at = comment.get("created_at", "Unknown date")
        comment_text = comment.get("comment", "")
        spoiler = comment.get("spoiler", False)
        review = comment.get("review", False)
        replies_count = comment.get("replies", 0)
        likes = comment.get("likes", 0)
        comment_id = comment.get("id", "")

        try:
            created_time = created_at.replace("Z", "").split(".")[0].replace("T", " ")
        except Exception:
            created_time = created_at

        comment_type = ""
        if review:
            comment_type = " [REVIEW]"
        if spoiler:
            comment_type += " [SPOILER]"

        result = f"# Comment by {username}{comment_type}\n\n"

        if show_spoilers:
            result += "**Note: Showing all spoilers**\n\n"
        else:
            result += "**Note: Spoilers are hidden. Use `show_spoilers=True` to view them.**\n\n"

        result += f"**Posted:** {created_time}\n\n"

        if (spoiler or "[spoiler]" in comment_text) and not show_spoilers:
            result += "**⚠️ SPOILER WARNING ⚠️**\n\n"
            result += "*This comment contains spoilers. Use `show_spoilers=True` to view it.*\n\n"
        else:
            if show_spoilers:
                comment_text = comment_text.replace("[spoiler]", "")
                comment_text = comment_text.replace("[/spoiler]", "")

            result += f"{comment_text}\n\n"

        result += f"*Likes: {likes} | Replies: {replies_count} | ID: {comment_id}*\n\n"

        if with_replies and replies:
            result += "## Replies\n\n"

            for reply in replies:
                reply_username = reply.get("user", {}).get("username", "Anonymous")
                reply_created_at = reply.get("created_at", "Unknown date")
                reply_text = reply.get("comment", "")
                reply_spoiler = reply.get("spoiler", False)
                reply_id = reply.get("id", "")

                try:
                    reply_time = (
                        reply_created_at.replace("Z", "")
                        .split(".")[0]
                        .replace("T", " ")
                    )
                except Exception:
                    reply_time = reply_created_at

                reply_type = ""
                if reply.get("review", False):
                    reply_type = " [REVIEW]"
                if reply_spoiler:
                    reply_type += " [SPOILER]"

                result += f"### {reply_username}{reply_type} - {reply_time}\n"

                if (reply_spoiler or "[spoiler]" in reply_text) and not show_spoilers:
                    result += "**⚠️ SPOILER WARNING ⚠️**\n\n"
                    result += "*This reply contains spoilers. Use `show_spoilers=True` to view it.*\n\n"
                else:
                    if show_spoilers:
                        reply_text = reply_text.replace("[spoiler]", "")
                        reply_text = reply_text.replace("[/spoiler]", "")

                    result += f"{reply_text}\n\n"

                result += f"*ID: {reply_id}*\n\n"
                result += "---\n\n"

        return result
