"""Video formatting methods for the Trakt MCP server."""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.types.api_responses import VideoResponse


class VideoFormatters:
    """Helper class for formatting video-related data for MCP responses."""

    @staticmethod
    def format_videos_list(
        videos: list["VideoResponse"], title: str, embed_markdown: bool = True
    ) -> str:
        """Format videos with optional embedded markdown.

        Args:
            videos: List of video response data
            title: Title of the movie/show for context
            embed_markdown: Use embedded markdown syntax for videos (default: True)

        Returns:
            Formatted markdown text with videos grouped by type
        """
        if not videos:
            return f"# Videos for {title}\n\nNo videos available."

        lines = [f"# Videos for {title}\n"]

        # Group by type
        by_type: dict[str, list[VideoResponse]] = {}
        for video in videos:
            video_type = video.get("type", "unknown").title()
            by_type.setdefault(video_type, []).append(video)

        for video_type, type_videos in by_type.items():
            lines.append(f"## {video_type}s\n")

            # Sort by published date (parse ISO string)
            def get_published_date(video: "VideoResponse") -> datetime:
                try:
                    return datetime.fromisoformat(
                        video.get("published_at", "1970-01-01").replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    return datetime.min

            sorted_videos = sorted(type_videos, key=get_published_date, reverse=True)

            for video in sorted_videos:
                # Format video title
                title_text = video.get("title", "Unknown Video")
                lines.append(f"### {title_text}")

                # Format video link
                url = video.get("url", "")
                site = video.get("site", "unknown")

                if embed_markdown:
                    # Embedded markdown syntax
                    lines.append(f"[![{title_text}]({url})]({url})")
                else:
                    # Simple text link
                    lines.append(f"[▶️ Watch on {site.title()}]({url})")

                # Video metadata
                metadata: list[str] = []
                if video.get("official"):
                    metadata.append("**Official**")

                if size := video.get("size"):
                    metadata.append(f"{size}p")

                if language := video.get("language"):
                    metadata.append(language.upper())

                if country := video.get("country"):
                    metadata.append(f"({country.upper()})")

                # Format publication date
                if published_at := video.get("published_at"):
                    try:
                        date_obj = datetime.fromisoformat(
                            published_at.replace("Z", "+00:00")
                        )
                        metadata.append(f"*{date_obj.strftime('%B %d, %Y')}*")
                    except (ValueError, TypeError):
                        metadata.append("*Date unknown*")

                lines.append(" • ".join(metadata))
                lines.append("")  # Empty line between videos

        return "\n".join(lines)
