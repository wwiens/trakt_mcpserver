"""Tests for VideoFormatters class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from models.formatters.videos import VideoFormatters

if TYPE_CHECKING:
    from models.types.api_responses import VideoResponse, VideoSite, VideoType


def make_video_response(
    *,
    title: str = "Unknown Video",
    url: str = "https://youtube.com/watch?v=ABC123DEF12",
    site: VideoSite = "youtube",
    type_: VideoType = "trailer",
    size: int = 1080,
    official: bool = True,
    published_at: str = "2025-01-01T00:00:00.000Z",
    country: str = "us",
    language: str = "en",
    **overrides: Any,
) -> VideoResponse:
    """Factory helper for creating VideoResponse test data."""
    base: VideoResponse = {
        "title": title,
        "url": url,
        "site": site,
        "type": type_,
        "size": size,
        "official": official,
        "published_at": published_at,
        "country": country,
        "language": language,
    }
    return cast("VideoResponse", {**base, **overrides})


class TestVideoFormatters:
    """Test cases for VideoFormatters class."""

    def test_class_exists(self):
        """Test that VideoFormatters class exists."""
        assert VideoFormatters is not None

    def test_all_methods_are_static(self):
        """Test that all methods are static methods."""
        # Check that methods don't require instance
        assert callable(VideoFormatters.extract_youtube_video_id)
        assert callable(VideoFormatters.get_youtube_embed_url)
        assert callable(VideoFormatters.get_video_thumbnail_url)
        assert callable(VideoFormatters.format_videos_list)

    def test_extract_youtube_video_id_standard_format(self):
        """Test YouTube video ID extraction from standard URL format."""
        url = "https://youtube.com/watch?v=ZbsiKjVAV28"
        extract_fn = VideoFormatters.extract_youtube_video_id
        video_id = extract_fn(url)
        assert video_id == "ZbsiKjVAV28"

    def test_extract_youtube_video_id_www_format(self):
        """Test YouTube video ID extraction from www URL format."""
        url = "https://www.youtube.com/watch?v=ZbsiKjVAV28"
        extract_fn = VideoFormatters.extract_youtube_video_id
        video_id = extract_fn(url)
        assert video_id == "ZbsiKjVAV28"

    def test_extract_youtube_video_id_short_format(self):
        """Test YouTube video ID extraction from short URL format."""
        url = "https://youtu.be/ZbsiKjVAV28"
        extract_fn = VideoFormatters.extract_youtube_video_id
        video_id = extract_fn(url)
        assert video_id == "ZbsiKjVAV28"

    def test_extract_youtube_video_id_embed_format(self):
        """Test YouTube video ID extraction from embed URL format."""
        url = "https://youtube.com/embed/ZbsiKjVAV28"
        extract_fn = VideoFormatters.extract_youtube_video_id
        video_id = extract_fn(url)
        assert video_id == "ZbsiKjVAV28"

    def test_extract_youtube_video_id_with_additional_params(self):
        """Test YouTube video ID extraction with additional URL parameters."""
        url = "https://youtube.com/watch?v=ZbsiKjVAV28&t=123&list=xyz"
        extract_fn = VideoFormatters.extract_youtube_video_id
        video_id = extract_fn(url)
        assert video_id == "ZbsiKjVAV28"

    def test_extract_youtube_video_id_mobile_format(self):
        """Test YouTube video ID extraction from mobile URL format."""
        url = "https://m.youtube.com/watch?v=ZbsiKjVAV28"
        extract_fn = VideoFormatters.extract_youtube_video_id
        video_id = extract_fn(url)
        assert video_id == "ZbsiKjVAV28"

    def test_extract_youtube_video_id_shorts_format(self):
        """Test YouTube video ID extraction from YouTube Shorts format."""
        url = "https://youtube.com/shorts/ZbsiKjVAV28"
        extract_fn = VideoFormatters.extract_youtube_video_id
        video_id = extract_fn(url)
        assert video_id == "ZbsiKjVAV28"

    def test_extract_youtube_video_id_nocookie_shorts_format(self):
        """Test YouTube video ID extraction from YouTube nocookie shorts format."""
        url = "https://youtube-nocookie.com/shorts/ZbsiKjVAV28"
        extract_fn = VideoFormatters.extract_youtube_video_id
        video_id = extract_fn(url)
        assert video_id == "ZbsiKjVAV28"

    def test_extract_youtube_video_id_invalid_url(self):
        """Test YouTube video ID extraction with invalid URL."""
        invalid_urls = [
            "https://example.com/video",
            "not-a-url",
            "",
            "https://youtube.com/watch?v=ABC",  # Too short
            "https://youtube.com/watch?v=ABC123TOOLONGFORVALIDID",  # Too long
        ]
        extract_fn = VideoFormatters.extract_youtube_video_id
        for url in invalid_urls:
            video_id = extract_fn(url)
            assert video_id is None

        # Test None separately
        video_id = extract_fn(None)  # type: ignore[arg-type]
        assert video_id is None

    def test_get_youtube_embed_url_valid(self):
        """Test YouTube embed URL generation with valid video ID."""
        url = "https://youtube.com/watch?v=ZbsiKjVAV28"
        embed_fn = VideoFormatters.get_youtube_embed_url
        embed_url = embed_fn(url)
        assert embed_url == "https://www.youtube-nocookie.com/embed/ZbsiKjVAV28"

    def test_get_youtube_embed_url_invalid(self):
        """Test YouTube embed URL generation with invalid URL."""
        url = "https://example.com/video"
        embed_fn = VideoFormatters.get_youtube_embed_url
        embed_url = embed_fn(url)
        assert embed_url is None

    def test_validate_embed_url_exact_matches(self):
        """Test URL validation for exact YouTube domain matches."""
        # Test private method via get_youtube_embed_url
        test_cases = [
            ("https://youtube.com/embed/ZbsiKjVAV28", True),
            ("https://youtube-nocookie.com/embed/ZbsiKjVAV28", True),
        ]

        for test_url, should_be_valid in test_cases:
            result = VideoFormatters.validate_embed_url(test_url)
            assert result == should_be_valid, f"Failed for {test_url}"

    def test_validate_embed_url_subdomain_matches(self):
        """Test URL validation for YouTube subdomain matches."""
        valid_subdomains = [
            "https://www.youtube.com/embed/ZbsiKjVAV28",
            "https://m.youtube.com/embed/ZbsiKjVAV28",
            "https://music.youtube.com/embed/ZbsiKjVAV28",
            "https://gaming.youtube.com/embed/ZbsiKjVAV28",
            "https://www.youtube-nocookie.com/embed/ZbsiKjVAV28",
        ]

        for test_url in valid_subdomains:
            result = VideoFormatters.validate_embed_url(test_url)
            assert result, f"Failed for valid subdomain: {test_url}"

    def test_validate_embed_url_invalid_domains(self):
        """Test URL validation rejects malicious or invalid domains."""
        invalid_domains = [
            "https://youtube.com.evil.com/embed/ZbsiKjVAV28",
            "https://youtube-nocookie.com.malicious.org/embed/ZbsiKjVAV28",
            "https://fakeyoutube.com/embed/ZbsiKjVAV28",
            "https://youtube.co/embed/ZbsiKjVAV28",
            "https://evil-youtube.com/embed/ZbsiKjVAV28",
            "http://youtube.com/embed/ZbsiKjVAV28",  # http instead of https
            "https://youtube.com:8080/embed/ZbsiKjVAV28",  # with port
        ]

        for test_url in invalid_domains:
            result = VideoFormatters.validate_embed_url(test_url)
            assert not result, f"Should reject invalid domain: {test_url}"

    def test_validate_embed_url_country_tlds(self):
        """Test URL validation for YouTube country TLD domains."""
        valid_country_domains = [
            "https://youtube.de/embed/ZbsiKjVAV28",  # Germany
            "https://youtube.fr/embed/ZbsiKjVAV28",  # France
            "https://youtube.co.uk/embed/ZbsiKjVAV28",  # UK
            "https://youtube.com.au/embed/ZbsiKjVAV28",  # Australia
            "https://youtube.com.mx/embed/ZbsiKjVAV28",  # Mexico
            "https://www.youtube.de/embed/ZbsiKjVAV28",  # Germany with www
            "https://m.youtube.fr/embed/ZbsiKjVAV28",  # France mobile
            "https://www.youtube.co.uk/embed/ZbsiKjVAV28",  # UK with www
            "https://www.youtube.com.au/embed/ZbsiKjVAV28",  # Australia with www
        ]

        for test_url in valid_country_domains:
            result = VideoFormatters.validate_embed_url(test_url)
            assert result, f"Failed for valid country domain: {test_url}"

    def test_validate_embed_url_invalid_country_patterns(self):
        """Test URL validation rejects invalid country TLD patterns."""
        invalid_country_domains = [
            "https://youtube.com.evil.com/embed/ZbsiKjVAV28",  # Still malicious
            "https://youtube.toolong/embed/ZbsiKjVAV28",  # TLD too long
            "https://youtube.123/embed/ZbsiKjVAV28",  # Numeric TLD
            "https://youtube.c/embed/ZbsiKjVAV28",  # TLD too short
            "https://fakeyoutube.de/embed/ZbsiKjVAV28",  # Wrong base domain
            "https://youtube.evil.de/embed/ZbsiKjVAV28",  # Extra subdomain before country
        ]

        for test_url in invalid_country_domains:
            result = VideoFormatters.validate_embed_url(test_url)
            assert not result, f"Should reject invalid country pattern: {test_url}"

    def test_get_video_thumbnail_url_youtube(self):
        """Test thumbnail URL generation for YouTube videos."""
        url = "https://youtube.com/watch?v=ZbsiKjVAV28"
        thumbnail_fn = VideoFormatters.get_video_thumbnail_url
        thumbnail_url = thumbnail_fn(url, "youtube")
        assert (
            thumbnail_url == "https://img.youtube.com/vi/ZbsiKjVAV28/maxresdefault.jpg"
        )

    def test_get_video_thumbnail_url_non_youtube(self):
        """Test thumbnail URL generation for non-YouTube videos."""
        url = "https://vimeo.com/123456789"
        thumbnail_fn = VideoFormatters.get_video_thumbnail_url
        thumbnail_url = thumbnail_fn(url, "vimeo")
        assert thumbnail_url == url  # Should return original URL

    def test_format_videos_list_empty(self):
        """Test video formatting with empty list."""
        videos: list[VideoResponse] = []
        result = VideoFormatters.format_videos_list(videos, "Test Movie")
        assert "# Videos for Test Movie" in result
        assert "No videos available." in result

    def test_format_videos_list_with_youtube_embed_true(self):
        """Test video formatting with YouTube video and embed_markdown=True."""
        videos = [
            make_video_response(
                title="Official Trailer",
                url="https://youtube.com/watch?v=ZbsiKjVAV28",
                site="youtube",
                type_="trailer",
                size=1080,
                official=True,
                published_at="2025-06-05T00:00:00.000Z",
                country="us",
                language="en",
            )
        ]

        result = VideoFormatters.format_videos_list(
            videos, "Test Movie", embed_markdown=True
        )

        # Check structure
        assert "# Videos for Test Movie" in result
        assert "## Trailers" in result
        assert "### Official Trailer" in result

        # Check iframe embed
        assert "<!-- Preserve iframe HTML below -->" in result
        assert "<iframe" in result
        assert "https://www.youtube-nocookie.com/embed/ZbsiKjVAV28" in result
        assert 'width="560"' in result
        assert 'height="315"' in result
        assert "allowfullscreen" in result

        # Check metadata
        assert "**Official**" in result
        assert "1080p" in result
        assert "EN" in result
        assert "(US)" in result
        assert "*June 05, 2025*" in result

    def test_format_videos_list_with_youtube_embed_false(self):
        """Test video formatting with YouTube video and embed_markdown=False."""
        videos = [
            make_video_response(
                title="Official Trailer",
                url="https://youtube.com/watch?v=ZbsiKjVAV28",
                site="youtube",
                type_="trailer",
                size=1080,
                official=True,
                published_at="2025-06-05T00:00:00.000Z",
                country="us",
                language="en",
            )
        ]

        result = VideoFormatters.format_videos_list(
            videos, "Test Movie", embed_markdown=False
        )

        # Should not contain iframe or instructional text
        assert "<!-- Preserve iframe HTML below -->" not in result
        assert "<iframe" not in result

        # Should contain simple link
        assert "[▶️ Watch on YouTube]" in result
        assert "https://youtube.com/watch?v=ZbsiKjVAV28" in result

    def test_format_videos_list_with_non_youtube_video(self):
        """Test video formatting with non-YouTube video."""
        videos = [
            make_video_response(
                title="Behind the Scenes",
                url="https://vimeo.com/123456789",
                site="vimeo",
                type_="featurette",
                size=720,
                official=False,
                published_at="2025-05-01T00:00:00.000Z",
                country="us",
                language="en",
            )
        ]

        result = VideoFormatters.format_videos_list(
            videos, "Test Movie", embed_markdown=True
        )

        # Should not contain iframe for non-YouTube
        assert "<!-- Preserve iframe HTML below -->" not in result
        assert "<iframe" not in result

        # Should contain simple link even with embed_markdown=True
        assert "[▶️ Watch on Vimeo]" in result
        assert "https://vimeo.com/123456789" in result

    def test_format_videos_list_multiple_types(self):
        """Test video formatting with multiple video types."""
        videos = [
            make_video_response(
                title="Official Trailer",
                url="https://youtube.com/watch?v=ABC123DEF12",
                site="youtube",
                type_="trailer",
                size=1080,
                official=True,
                published_at="2025-06-05T00:00:00.000Z",
                country="us",
                language="en",
            ),
            make_video_response(
                title="Teaser Trailer",
                url="https://youtube.com/watch?v=XYZ789ABC45",
                site="youtube",
                type_="teaser",
                size=720,
                official=True,
                published_at="2025-05-01T00:00:00.000Z",
                country="us",
                language="en",
            ),
        ]

        result = VideoFormatters.format_videos_list(
            videos, "Test Movie", embed_markdown=True
        )

        # Check both sections exist
        assert "## Trailers" in result
        assert "## Teasers" in result

        # Check both videos have iframe embeds
        assert result.count("<!-- Preserve iframe HTML below -->") == 2
        assert result.count("<iframe") == 2

    def test_format_videos_list_sorting_by_date(self):
        """Test that videos are sorted by publication date (newest first)."""
        videos = [
            make_video_response(
                title="Older Video",
                url="https://youtube.com/watch?v=OLD123456789",
                site="youtube",
                type_="trailer",
                published_at="2025-01-01T00:00:00.000Z",
            ),
            make_video_response(
                title="Newer Video",
                url="https://youtube.com/watch?v=NEW123456789",
                site="youtube",
                type_="trailer",
                published_at="2025-06-01T00:00:00.000Z",
            ),
        ]

        result = VideoFormatters.format_videos_list(
            videos, "Test Movie", embed_markdown=True
        )

        # Newer video should appear first
        newer_pos = result.find("Newer Video")
        older_pos = result.find("Older Video")
        assert newer_pos < older_pos

    def test_format_videos_list_invalid_date_handling(self):
        """Test handling of invalid publication dates."""
        videos = [
            make_video_response(
                title="Video with Bad Date",
                url="https://youtube.com/watch?v=ABC123DEF12",
                site="youtube",
                type_="trailer",
                published_at="invalid-date",
            )
        ]

        result = VideoFormatters.format_videos_list(
            videos, "Test Movie", embed_markdown=True
        )

        # Should not crash and should include the video
        assert "Video with Bad Date" in result
        assert "<iframe" in result

    def test_format_videos_list_missing_metadata(self):
        """Test video formatting with missing metadata fields."""
        videos = [
            make_video_response(
                title="Minimal Video",
                url="https://youtube.com/watch?v=ABC123DEF12",
                site="youtube",
                type_="trailer",
                # Missing many optional fields - using defaults from factory
            )
        ]

        result = VideoFormatters.format_videos_list(
            videos, "Test Movie", embed_markdown=True
        )

        # Should still work and contain the video
        assert "Minimal Video" in result
        assert "<iframe" in result
        assert "https://www.youtube-nocookie.com/embed/ABC123DEF12" in result

    def test_format_videos_list_youtube_extraction_failure(self):
        """Test handling when YouTube video ID extraction fails."""
        videos = [
            make_video_response(
                title="Bad YouTube URL",
                url="https://youtube.com/watch?v=INVALID",  # Too short
                site="youtube",
                type_="trailer",
            )
        ]

        result = VideoFormatters.format_videos_list(
            videos, "Test Movie", embed_markdown=True
        )

        # Should fallback to simple link, not iframe
        assert "<!-- Preserve iframe HTML below -->" not in result
        assert "<iframe" not in result
        assert "[▶️ Watch on YouTube]" in result
        assert "https://youtube.com/watch?v=INVALID" in result
