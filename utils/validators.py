"""Shared Pydantic validator helpers."""

from typing import Annotated

from pydantic import BeforeValidator


def strip_if_string(v: object) -> object:
    """Strip whitespace if the value is a string; otherwise return unchanged."""
    return v.strip() if isinstance(v, str) else v


StrippedStr = Annotated[str, BeforeValidator(strip_if_string)]
"""String field that strips leading/trailing whitespace before validation."""
