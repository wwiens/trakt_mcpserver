"""Mixin for limit and page validation in Pydantic models."""

from typing import Self

from pydantic import BaseModel, model_validator


class LimitPageValidatorMixin(BaseModel):
    """Mixin that validates limit=0 is not used with explicit page.

    This mixin provides a model validator that ensures limit=0 (fetch all mode)
    is only used with auto-pagination (page=None), not with explicit page numbers.

    Classes using this mixin must define:
        - limit: int field
        - page: int | None field
    """

    limit: int
    page: int | None

    @model_validator(mode="after")
    def _validate_limit_with_page(self) -> Self:
        """Validate that limit=0 requires auto-pagination (page=None)."""
        if self.page is not None and self.limit == 0:
            raise ValueError(
                "limit must be > 0 when page is specified; limit=0 (fetch all) "
                + "requires auto-pagination"
            )
        return self
