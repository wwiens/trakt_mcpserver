"""Base classes and mixins for MCP server components."""

from .error_mixin import ToolErrors
from .identifier_mixin import IdentifierValidatorMixin
from .limit_page_mixin import LimitPageValidatorMixin
from .params import (
    CommentIdParam,
    EpisodeIdParam,
    LimitOnly,
    MovieIdParam,
    PeriodParams,
    PersonIdParam,
    SeasonIdParam,
    ShowIdParam,
)

__all__ = [
    "CommentIdParam",
    "EpisodeIdParam",
    "IdentifierValidatorMixin",
    "LimitOnly",
    "LimitPageValidatorMixin",
    "MovieIdParam",
    "PeriodParams",
    "PersonIdParam",
    "SeasonIdParam",
    "ShowIdParam",
    "ToolErrors",
]
