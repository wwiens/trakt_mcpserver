"""Video formatting methods for the Trakt MCP server."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from html import escape
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from pydantic import ValidationError

from models.videos.video import ValidatedVideo

if TYPE_CHECKING:
    from models.types.api_responses import VideoResponse

# Pre-compiled regex patterns for YouTube video ID extraction
_YT_PATTERNS = [
    # YouTube domains (youtube.com, youtube-nocookie.com) with all path formats
    re.compile(
        r"(?:https?://)?(?:(?:www|m)\.)?youtube(?:-nocookie)?\.com/"
        + r"(?:watch\?(?:[^&]*&)*v=|embed/|shorts/)([A-Za-z0-9_-]{11})(?=[?#&/\s]|$)"
    ),
    # youtu.be short URLs
    re.compile(
        r"(?:https?://)?(?:(?:www|m)\.)?youtu\.be/([A-Za-z0-9_-]{11})(?=[?#&/\s]|$)"
    ),
]


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
        url = url.strip()

        # Use pre-compiled patterns for better performance
        for pattern in _YT_PATTERNS:
            match = pattern.search(url)
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
    def escape_markdown(text: str) -> str:
        """Escape Markdown characters to prevent formatting injection.

        Args:
            text: Text that may contain Markdown characters

        Returns:
            Text with Markdown characters escaped
        """
        # Escape backslash first to avoid double-escaping newly added backslashes
        replacements = [
            ("\\", r"\\"),
            ("`", r"\`"),
            ("*", r"\*"),
            ("_", r"\_"),
            ("{", r"\{"),
            ("}", r"\}"),
            ("[", r"\["),
            ("]", r"\]"),
            ("(", r"\("),
            (")", r"\)"),
            ("#", r"\#"),
            ("+", r"\+"),
            ("-", r"\-"),
            (".", r"\."),
            ("!", r"\!"),
            ("|", r"\|"),
            (">", r"\>"),
        ]
        for a, b in replacements:
            text = text.replace(a, b)
        return text

    @staticmethod
    def parse_iso_datetime(date_string: str | None) -> datetime | None:
        """Parse ISO datetime string with Z timezone.

        Args:
            date_string: ISO datetime string, possibly with 'Z' timezone

        Returns:
            Timezone-aware datetime in UTC or None if parsing fails
        """
        if not date_string:
            return None
        try:
            # Parse datetime and ensure it's timezone-aware in UTC
            dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
            # If somehow still naive, assume UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            # Convert to UTC if not already
            return dt.astimezone(UTC)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_embed_url(url: str) -> bool:
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
            # Only allow explicit embed paths
            if not parsed.path.startswith("/embed/"):
                return False
            # Only allow trusted YouTube embed domains (wildcard-based + country TLDs)
            domain = parsed.netloc.lower()

            # Standard domains
            if (
                domain == "youtube.com"
                or domain == "youtube-nocookie.com"
                or domain.endswith(".youtube.com")
                or domain.endswith(".youtube-nocookie.com")
            ):
                return True

            # Country TLD patterns: youtube.[cc], youtube.com.[cc], youtube.co.[cc]
            country_patterns = [
                r"^youtube\.(?!co$)[a-z]{2}$",  # youtube.de, youtube.fr (exclude youtube.co)
                r"^youtube\.com\.[a-z]{2}$",  # youtube.com.au, youtube.com.mx
                r"^youtube\.co\.[a-z]{2}$",  # youtube.co.uk, youtube.co.jp (requires country code)
                r"^[a-z0-9-]+\.youtube\.(?!co$)[a-z]{2}$",  # www.youtube.de (exclude .co)
                r"^[a-z0-9-]+\.youtube\.com\.[a-z]{2}$",  # www.youtube.com.au
                r"^[a-z0-9-]+\.youtube\.co\.[a-z]{2}$",  # www.youtube.co.uk
            ]

            return any(re.match(pattern, domain) for pattern in country_patterns)
        except Exception:
            return False

    @staticmethod
    def validate_watch_url(url: str) -> str | None:
        """Validate that watch URL uses safe schemes (http/https only).

        Args:
            url: URL to validate for safety

        Returns:
            Original URL if safe, None if unsafe or malformed
        """
        if not url:
            return None
        try:
            parsed = urlparse(url)
            # Only allow absolute http(s) URLs with a host and no whitespace
            if any(ch.isspace() for ch in url):
                return None
            if parsed.scheme in ("http", "https") and parsed.netloc:
                return url
            return None
        except Exception:
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
            # Use standard YouTube embed URL
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            # Validate the constructed URL before returning
            if VideoFormatters.validate_embed_url(embed_url):
                return embed_url
        return None

    @staticmethod
    def validate_video_list(videos: list[dict[str, Any]]) -> list[ValidatedVideo]:
        """Validate a list of video dictionaries using Pydantic models.

        Args:
            videos: List of video data dictionaries from API responses

        Returns:
            List of validated video models

        Raises:
            ValueError: If any video fails validation with details
        """
        if not videos:
            return []

        validated_videos: list[ValidatedVideo] = []
        validation_errors: list[str] = []

        for i, video in enumerate(videos):
            try:
                validated_video = ValidatedVideo.model_validate(video)
                validated_videos.append(validated_video)
            except ValidationError as e:
                error_details: list[str] = []
                for error in e.errors():
                    field = ".".join(str(loc) for loc in error["loc"])
                    message = error["msg"]
                    error_details.append(f"{field}: {message}")
                validation_errors.append(f"Video {i}: {'; '.join(error_details)}")

        if validation_errors:
            raise ValueError(
                f"Video validation failed: {' | '.join(validation_errors)}"
            )

        return validated_videos

    @staticmethod
    def format_videos_list(
        videos: list[VideoResponse],
        title: str,
        embed_markdown: bool = True,
        validate_input: bool = True,
    ) -> str:
        """Format videos with optional embedded markdown.

        Args:
            videos: List of video response data
            title: Title of the movie/show for context
            embed_markdown: Use embedded markdown syntax for videos (default: True)
            validate_input: Whether to validate input data with Pydantic models (default: True)

        Returns:
            Formatted markdown text with videos grouped by type

        Raises:
            ValueError: If validate_input=True and video data is invalid
        """
        # Validate inputs if requested (follows project guideline: "Validate all inputs with Pydantic models")
        if validate_input and videos:
            try:
                # Convert VideoResponse TypedDicts to plain dicts for validation
                video_dicts = [dict(video) for video in videos]
                VideoFormatters.validate_video_list(video_dicts)
            except ValueError as e:
                raise ValueError(f"Invalid video data provided: {e}") from e
        if not videos:
            return f"# Videos for {title}\n\nNo videos available."

        lines = [f"# Videos for {title}\n"]

        by_type: dict[str, list[VideoResponse]] = {}
        for video in videos:
            video_type = video.get("type", "unknown").title()
            by_type.setdefault(video_type, []).append(video)

        for video_type in sorted(by_type):
            lines.append(f"## {video_type}s\n")
            type_videos = by_type[video_type]

            def get_published_date(video: VideoResponse) -> datetime:
                parsed_date = VideoFormatters.parse_iso_datetime(
                    video.get("published_at")
                )
                return parsed_date or datetime.min.replace(tzinfo=UTC)

            sorted_videos = sorted(type_videos, key=get_published_date, reverse=True)

            for video in sorted_videos:
                raw_title = video.get("title", "Unknown Video")
                title_text = VideoFormatters.escape_markdown(raw_title)
                lines.append(f"### {title_text}")

                # Format video link
                url = video.get("url", "")
                site = video.get("site", "unknown")

                if embed_markdown:
                    # Generate HTML iframe for YouTube videos, fallback to markdown for others
                    if site.lower() == "youtube":
                        embed_url = VideoFormatters.get_youtube_embed_url(url)
                        if embed_url:
                            lines.append("Preserve iframe HTML below")
                            iframe_html = (
                                f'<iframe width="560" height="315" src="{escape(embed_url, quote=True)}" '
                                f'title="YouTube video player" frameborder="0" '
                                f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                                f'gyroscope; picture-in-picture; web-share" '
                                f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
                            )
                            lines.append(iframe_html)
                        else:
                            # Fallback to markdown link if embed URL extraction fails
                            site_display = VideoFormatters.normalize_site_name(site)
                            safe_url = VideoFormatters.validate_watch_url(url)
                            if safe_url:
                                lines.append(
                                    f"[▶️ Watch on {site_display}](<{safe_url}>)"
                                )
                            else:
                                lines.append("Watch link unavailable")
                    else:
                        # For non-YouTube videos, use simple markdown link
                        site_display = VideoFormatters.normalize_site_name(site)
                        safe_url = VideoFormatters.validate_watch_url(url)
                        if safe_url:
                            lines.append(f"[▶️ Watch on {site_display}](<{safe_url}>)")
                        else:
                            lines.append("Watch link unavailable")
                else:
                    # Simple text link
                    site_display = VideoFormatters.normalize_site_name(site)
                    safe_url = VideoFormatters.validate_watch_url(url)
                    if safe_url:
                        lines.append(f"[▶️ Watch on {site_display}](<{safe_url}>)")
                    else:
                        lines.append("Watch link unavailable")

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

                if metadata:
                    lines.append(" • ".join(metadata))
                lines.append("")  # Empty line between videos

        return "\n".join(lines)
