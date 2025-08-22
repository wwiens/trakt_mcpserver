"""Video formatting methods for the Trakt MCP server."""

import html
import re
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlparse

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
    def normalize_site_name(site: str) -> str:
        """Normalize video site display names for consistent UX.

        Args:
            site: Site name from API response

        Returns:
            Normalized display name
        """
        site_mapping = {
            "youtube": "YouTube",
        }
        return site_mapping.get(site.lower(), site.title())

    @staticmethod
    def parse_iso_datetime(date_string: str | None) -> datetime | None:
        """Parse ISO datetime string with Z timezone.

        Args:
            date_string: ISO datetime string, possibly with 'Z' timezone

        Returns:
            Parsed datetime or None if parsing fails
        """
        if not date_string:
            return None
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _validate_embed_url(url: str) -> bool:
        """Validate that embed URL is from trusted domains with safe schemes.

        Args:
            url: URL to validate

        Returns:
            True if URL is safe for embedding, False otherwise
        """
        try:
            parsed = urlparse(url)
            # Only allow https scheme for embed URLs
            if parsed.scheme != "https":
                return False
            # Only allow trusted embed domains
            allowed_domains = {"www.youtube.com", "youtube.com", "www.youtube-nocookie.com"}
            return parsed.netloc in allowed_domains
        except Exception:
            return False

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
            # Use youtube-nocookie.com for privacy-friendly embeds
            embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}"
            # Validate the constructed URL before returning
            if VideoFormatters._validate_embed_url(embed_url):
                return embed_url
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
                parsed_date = VideoFormatters.parse_iso_datetime(
                    video.get("published_at")
                )
                return parsed_date or datetime.min

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
                            lines.append("<!-- Preserve iframe HTML below -->")
                            # HTML-escape the embed URL to prevent XSS
                            escaped_url = html.escape(embed_url, quote=True)
                            iframe_html = (
                                f'<iframe width="560" height="315" src="{escaped_url}" '
                                f'frameborder="0" allow="accelerometer; autoplay; clipboard-write; '
                                f'encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
                            )
                            lines.append(iframe_html)
                        else:
                            # Fallback to markdown link if embed URL extraction fails
                            site_display = VideoFormatters.normalize_site_name(site)
                            lines.append(f"[▶️ Watch on {site_display}]({url})")
                    else:
                        # For non-YouTube videos, use simple markdown link
                        site_display = VideoFormatters.normalize_site_name(site)
                        lines.append(f"[▶️ Watch on {site_display}]({url})")
                else:
                    # Simple text link
                    site_display = VideoFormatters.normalize_site_name(site)
                    lines.append(f"[▶️ Watch on {site_display}]({url})")

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
                    date_obj = VideoFormatters.parse_iso_datetime(published_at)
                    if date_obj:
                        metadata.append(f"*{date_obj.strftime('%B %d, %Y')}*")
                    else:
                        metadata.append("*Date unknown*")

                lines.append(" • ".join(metadata))
                lines.append("")  # Empty line between videos

        return "\n".join(lines)
