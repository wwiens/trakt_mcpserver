"""Shared parameter models for MCP server tools."""

from typing import Literal

from pydantic import Field

from config.api import DEFAULT_LIMIT

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
