"""Pydantic models for video data validation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Type aliases for video data
VideoSite = Literal["youtube", "vimeo", "dailymotion", "metacafe"]
VideoType = Literal[
    "trailer", "teaser", "featurette", "clip", "behind_the_scenes", "gag_reel"
]


class ValidatedVideo(BaseModel):
    """Pydantic model for validating video data input.

    This ensures all video data is properly validated before formatting,
    following the project guideline: "Validate all inputs with Pydantic models."
    """

    title: str = Field(..., description="Video title")
    url: str = Field(..., min_length=1, description="Video URL")
    site: VideoSite = Field(..., description="Video hosting site")
    type: VideoType = Field(..., description="Type of video content")
    size: int = Field(..., gt=0, description="Video resolution (480, 720, 1080, etc.)")
    official: bool = Field(..., description="Whether this is official content")
    published_at: str = Field(..., min_length=1, description="ISO datetime string")
    country: str = Field(
        ..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"
    )
    language: str = Field(
        ..., min_length=2, max_length=2, description="ISO 639-1 language code"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace-only")
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format and safety."""
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")

        # Basic URL validation - more detailed validation happens in VideoFormatters
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")

        return v

    @field_validator("country")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate ISO 3166-1 alpha-2 country code format."""
        v = v.strip().upper()
        if len(v) != 2 or not v.isalpha():
            raise ValueError("Country must be a 2-letter ISO 3166-1 alpha-2 code")
        return v

    @field_validator("language")
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        """Validate ISO 639-1 language code format."""
        v = v.strip().lower()
        if len(v) != 2 or not v.isalpha():
            raise ValueError("Language must be a 2-letter ISO 639-1 code")
        return v
