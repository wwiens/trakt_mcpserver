"""Language code type for translation endpoints."""

import re
from typing import Final

LANGUAGE_PATTERN: Final[str] = r"^(all|[a-z]{2})$"

INVALID_LANGUAGE_MSG: Final[str] = (
    "Language must be 'all' or a 2-letter ISO 639-1 code (e.g., 'en', 'es')"
)


def validate_language(language: str) -> str:
    """Validate and normalize a language code.

    Args:
        language: Language code to validate

    Returns:
        Normalized lowercase language code

    Raises:
        ValueError: If language is not 'all' or a 2-letter code
    """
    normalized = language.strip().lower()
    if not re.match(LANGUAGE_PATTERN, normalized):
        msg = f"{INVALID_LANGUAGE_MSG}, got: '{language}'"
        raise ValueError(msg)
    return normalized
