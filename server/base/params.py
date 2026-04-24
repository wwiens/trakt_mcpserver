"""Shared parameter models for MCP server tools."""

from typing import Literal

from pydantic import BaseModel, Field

from config.api import DEFAULT_LIMIT
from config.mcp.descriptions import (
    COMMENT_ID_DESCRIPTION,
    EPISODE_DESCRIPTION,
    MOVIE_ID_DESCRIPTION,
    PERSON_ID_DESCRIPTION,
    SEASON_DESCRIPTION,
    SHOW_ID_DESCRIPTION,
)
from utils.validators import StrippedStr

from .limit_page_mixin import LimitPageValidatorMixin


class LimitOnly(LimitPageValidatorMixin):
    """Parameters for tools that only require a limit."""

    limit: int = Field(
        DEFAULT_LIMIT,
        ge=0,
        le=100,
        description="Maximum results to return (0=all up to 100, default=10)",
    )
    page: int | None = Field(
        default=None, ge=1, description="Page number for pagination (optional)"
    )


class PeriodParams(LimitPageValidatorMixin):
    """Parameters for tools that accept limit and time period."""

    limit: int = Field(
        DEFAULT_LIMIT,
        ge=0,
        le=100,
        description="Maximum results to return (0=all up to 100, default=10)",
    )
    period: Literal["daily", "weekly", "monthly", "yearly", "all"] = "weekly"
    page: int | None = Field(
        default=None, ge=1, description="Page number for pagination (optional)"
    )


class ShowIdParam(BaseModel):
    """Parameters for tools that require a show ID."""

    show_id: StrippedStr = Field(
        ...,
        min_length=1,
        description=SHOW_ID_DESCRIPTION,
    )


class MovieIdParam(BaseModel):
    """Parameters for tools that require a movie ID."""

    movie_id: StrippedStr = Field(
        ...,
        min_length=1,
        description=MOVIE_ID_DESCRIPTION,
    )


class PersonIdParam(BaseModel):
    """Parameters for tools that require a person ID."""

    person_id: StrippedStr = Field(
        ...,
        min_length=1,
        description=PERSON_ID_DESCRIPTION,
    )


class SeasonIdParam(BaseModel):
    """Parameters for tools that require a show ID and season number."""

    show_id: StrippedStr = Field(
        ...,
        min_length=1,
        description=SHOW_ID_DESCRIPTION,
    )
    season: int = Field(
        ...,
        ge=0,
        description=SEASON_DESCRIPTION,
    )


class EpisodeIdParam(SeasonIdParam):
    """Parameters for tools that require a show ID, season, and episode number."""

    episode: int = Field(
        ...,
        ge=1,
        description=EPISODE_DESCRIPTION,
    )


class CommentIdParam(BaseModel):
    """Parameters for tools that require a comment ID."""

    comment_id: StrippedStr = Field(
        ...,
        min_length=1,
        description=COMMENT_ID_DESCRIPTION,
    )
