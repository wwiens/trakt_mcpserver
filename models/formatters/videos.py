"""Video formatting methods for the Trakt MCP server."""

import re
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.types.api_responses import VideoResponse


class VideoFormatters:
    """Helper class for formatting video-related data for MCP responses."""

    @staticmethod
    def extract_youtube_video_id(url: str) -> str | None:
        """Extract YouTube video ID from various URL formats.

        Args:
            url: YouTube URL in various formats

        Returns:
            Video ID if found, None otherwise
        """
        if not url:
            return None

        # Handle different YouTube URL formats - ensure exactly 11 characters
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})(?:[&\s]|$)",
            r"youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})(?:[&\s]|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    @staticmethod
    def get_youtube_embed_url(url: str) -> str | None:
        """Get YouTube embed URL from various YouTube URL formats.

        Args:
            url: YouTube URL in various formats

        Returns:
            YouTube embed URL or None if not a YouTube video
        """
        video_id = VideoFormatters.extract_youtube_video_id(url)
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None

    @staticmethod
    def get_video_thumbnail_url(url: str, site: str) -> str:
        """Get thumbnail URL for video.

        Args:
            url: Video URL
            site: Video site (youtube, vimeo, etc.)

        Returns:
            Thumbnail URL or original URL if no thumbnail available
        """
        if site.lower() == "youtube":
            video_id = VideoFormatters.extract_youtube_video_id(url)
            if video_id:
                return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        # For other sites or if extraction fails, return original URL
        return url

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
                    # Generate HTML iframe for YouTube videos, fallback to markdown for others
                    if site.lower() == "youtube":
                        embed_url = VideoFormatters.get_youtube_embed_url(url)
                        if embed_url:
                            # Add explicit instructional text for LLM to preserve iframe HTML
                            lines.append(
                                "🎥 **PRESERVE THIS IFRAME HTML** - DO NOT convert to markdown links. Display this exact HTML iframe code in your response. Users can watch the video directly here."
                            )
                            iframe_html = (
                                f'<iframe width="560" height="315" src="{embed_url}" '
                                f'frameborder="0" allow="accelerometer; autoplay; clipboard-write; '
                                f'encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
                            )
                            lines.append(iframe_html)
                        else:
                            # Fallback to markdown link if embed URL extraction fails
                            lines.append(f"[▶️ Watch on YouTube]({url})")
                    else:
                        # For non-YouTube videos, use simple markdown link
                        lines.append(f"[▶️ Watch on {site.title()}]({url})")
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
