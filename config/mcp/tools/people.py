"""People-specific MCP tool name definitions."""

from typing import Final

PEOPLE_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "fetch_person_summary",
        "fetch_person_movies",
        "fetch_person_shows",
        "fetch_person_lists",
    }
)
