"""Tests for video validation models."""

import pytest
from pydantic import ValidationError

from models.videos.video import ValidatedVideo


class TestValidatedVideo:
    """Tests for ValidatedVideo Pydantic model."""

    def test_valid_video_creation(self):
        """Test creating a valid video model."""
        video_data = {
            "title": "Official Trailer",
            "url": "https://youtube.com/watch?v=ABC123",
            "site": "youtube",
            "type": "trailer",
            "size": 1080,
            "official": True,
            "published_at": "2023-01-15T10:30:00Z",
            "country": "US",
            "language": "en",
        }

        video = ValidatedVideo.model_validate(video_data)

        assert video.title == "Official Trailer"
        assert video.url == "https://youtube.com/watch?v=ABC123"
        assert video.site == "youtube"
        assert video.type == "trailer"
        assert video.size == 1080
        assert video.official is True
        assert video.published_at == "2023-01-15T10:30:00Z"
        assert video.country == "US"
        assert video.language == "en"

    def test_url_validation(self):
        """Test URL validation rules."""
        base_data = {
            "title": "Test Video",
            "site": "youtube",
            "type": "trailer",
            "size": 1080,
            "official": True,
            "published_at": "2023-01-15T10:30:00Z",
            "country": "US",
            "language": "en",
        }

        # Valid URLs should pass
        valid_urls = [
            "https://youtube.com/watch?v=ABC123",
            "http://example.com/video.mp4",
            "https://vimeo.com/123456789",
        ]

        for url in valid_urls:
            video_data = {**base_data, "url": url}
            video = ValidatedVideo.model_validate(video_data)
            assert video.url == url

        # Invalid URLs should fail
        invalid_urls = [
            "",  # Empty
            "   ",  # Whitespace only
            "ftp://example.com/video",  # Wrong protocol
            "javascript:alert(1)",  # Dangerous protocol
            "not-a-url",  # Not a URL
        ]

        for url in invalid_urls:
            video_data = {**base_data, "url": url}
            with pytest.raises(ValidationError) as exc_info:
                ValidatedVideo.model_validate(video_data)
            assert "url" in str(exc_info.value)

    def test_country_code_validation(self):
        """Test country code validation."""
        base_data = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=ABC123",
            "site": "youtube",
            "type": "trailer",
            "size": 1080,
            "official": True,
            "published_at": "2023-01-15T10:30:00Z",
            "language": "en",
        }

        # Valid country codes should pass (and be normalized to uppercase)
        valid_countries = [
            ("us", "US"),
            ("UK", "UK"),
            ("de", "DE"),
            ("fr", "FR"),
        ]

        for input_country, expected_country in valid_countries:
            video_data = {**base_data, "country": input_country}
            video = ValidatedVideo.model_validate(video_data)
            assert video.country == expected_country

        # Invalid country codes should fail
        invalid_countries = [
            "",  # Empty
            "USA",  # Too long
            "U",  # Too short
            "12",  # Numbers
            "U1",  # Mixed
            "   ",  # Whitespace
        ]

        for country in invalid_countries:
            video_data = {**base_data, "country": country}
            with pytest.raises(ValidationError) as exc_info:
                ValidatedVideo.model_validate(video_data)
            assert "country" in str(exc_info.value)

    def test_language_code_validation(self):
        """Test language code validation."""
        base_data = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=ABC123",
            "site": "youtube",
            "type": "trailer",
            "size": 1080,
            "official": True,
            "published_at": "2023-01-15T10:30:00Z",
            "country": "US",
        }

        # Valid language codes should pass (and be normalized to lowercase)
        valid_languages = [
            ("EN", "en"),
            ("fr", "fr"),
            ("De", "de"),
            ("ES", "es"),
        ]

        for input_lang, expected_lang in valid_languages:
            video_data = {**base_data, "language": input_lang}
            video = ValidatedVideo.model_validate(video_data)
            assert video.language == expected_lang

        # Invalid language codes should fail
        invalid_languages = [
            "",  # Empty
            "eng",  # Too long
            "e",  # Too short
            "12",  # Numbers
            "e1",  # Mixed
            "   ",  # Whitespace
        ]

        for language in invalid_languages:
            video_data = {**base_data, "language": language}
            with pytest.raises(ValidationError) as exc_info:
                ValidatedVideo.model_validate(video_data)
            assert "language" in str(exc_info.value)

    def test_required_fields(self):
        """Test that all fields are required."""
        # Start with valid data and remove each field
        base_data = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=ABC123",
            "site": "youtube",
            "type": "trailer",
            "size": 1080,
            "official": True,
            "published_at": "2023-01-15T10:30:00Z",
            "country": "US",
            "language": "en",
        }

        required_fields = [
            "title",
            "url",
            "site",
            "type",
            "size",
            "official",
            "published_at",
            "country",
            "language",
        ]

        for field in required_fields:
            invalid_data = {k: v for k, v in base_data.items() if k != field}
            with pytest.raises(ValidationError) as exc_info:
                ValidatedVideo.model_validate(invalid_data)
            assert field in str(exc_info.value)

    def test_site_type_validation(self):
        """Test site and type literal validation."""
        base_data = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=ABC123",
            "size": 1080,
            "official": True,
            "published_at": "2023-01-15T10:30:00Z",
            "country": "US",
            "language": "en",
        }

        # Valid sites
        valid_sites = ["youtube", "vimeo", "dailymotion", "metacafe"]
        for site in valid_sites:
            video_data = {**base_data, "site": site, "type": "trailer"}
            video = ValidatedVideo.model_validate(video_data)
            assert video.site == site

        # Invalid site should fail
        with pytest.raises(ValidationError):
            ValidatedVideo.model_validate(
                {**base_data, "site": "invalid_site", "type": "trailer"}
            )

        # Valid types
        valid_types = [
            "trailer",
            "teaser",
            "featurette",
            "clip",
            "behind_the_scenes",
            "gag_reel",
        ]
        for video_type in valid_types:
            video_data = {**base_data, "site": "youtube", "type": video_type}
            video = ValidatedVideo.model_validate(video_data)
            assert video.type == video_type

        # Invalid type should fail
        with pytest.raises(ValidationError):
            ValidatedVideo.model_validate(
                {**base_data, "site": "youtube", "type": "invalid_type"}
            )

    def test_size_validation(self):
        """Test video size validation."""
        base_data = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=ABC123",
            "site": "youtube",
            "type": "trailer",
            "official": True,
            "published_at": "2023-01-15T10:30:00Z",
            "country": "US",
            "language": "en",
        }

        # Valid sizes (positive integers)
        valid_sizes = [480, 720, 1080, 1440, 2160]
        for size in valid_sizes:
            video_data = {**base_data, "size": size}
            video = ValidatedVideo.model_validate(video_data)
            assert video.size == size

        # Invalid sizes should fail
        invalid_sizes = [0, -1, -720]
        for size in invalid_sizes:
            video_data = {**base_data, "size": size}
            with pytest.raises(ValidationError) as exc_info:
                ValidatedVideo.model_validate(video_data)
            assert "size" in str(exc_info.value)

    def test_title_validation(self):
        """Test title validation."""
        base_data = {
            "url": "https://youtube.com/watch?v=ABC123",
            "site": "youtube",
            "type": "trailer",
            "size": 1080,
            "official": True,
            "published_at": "2023-01-15T10:30:00Z",
            "country": "US",
            "language": "en",
        }

        # Valid titles
        valid_titles = ["Official Trailer", "Behind the Scenes", "A"]
        for title in valid_titles:
            video_data = {**base_data, "title": title}
            video = ValidatedVideo.model_validate(video_data)
            assert video.title == title

        # Invalid titles should fail
        invalid_titles = ["", "   "]  # Empty or whitespace-only
        for title in invalid_titles:
            video_data = {**base_data, "title": title}
            with pytest.raises(ValidationError) as exc_info:
                ValidatedVideo.model_validate(video_data)
            assert "title" in str(exc_info.value)
