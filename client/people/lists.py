"""Person lists functionality."""

from config.api import DEFAULT_LIMIT
from models.types import ListItemResponse
from utils.api.errors import handle_api_errors

from ..base import BaseClient
from .utils import build_person_endpoint, validate_person_id

VALID_LIST_TYPES = frozenset({"all", "personal", "official", "watchlists"})
VALID_LIST_SORTS = frozenset(
    {"popular", "likes", "comments", "items", "added", "updated"}
)


class PersonListsClient(BaseClient):
    """Client for person lists operations."""

    @handle_api_errors
    async def get_person_lists(
        self,
        person_id: str,
        list_type: str = "all",
        sort: str = "popular",
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
    ) -> list[ListItemResponse]:
        """Get lists containing a specific person.

        Args:
            person_id: Trakt ID, Trakt slug, or IMDB ID
            list_type: List type filter (all, personal, official, watchlists)
            sort: Sort order (popular, likes, comments, items, added, updated)
            limit: Number of results to return
            page: Page number (None for auto-pagination)

        Returns:
            List of lists containing this person
        """
        person_id = validate_person_id(person_id)

        if list_type not in VALID_LIST_TYPES:
            msg = (
                f"Invalid list_type '{list_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_LIST_TYPES))}"
            )
            raise ValueError(msg)

        if sort not in VALID_LIST_SORTS:
            msg = (
                f"Invalid sort '{sort}'. "
                f"Must be one of: {', '.join(sorted(VALID_LIST_SORTS))}"
            )
            raise ValueError(msg)

        endpoint = build_person_endpoint(
            "person_lists", person_id, type=list_type, sort=sort
        )

        if page is not None:
            params = {"page": page, "limit": limit}
            response = await self._make_paginated_request(
                endpoint,
                response_type=ListItemResponse,
                params=params,
            )
            return list(response.data)

        return await self.auto_paginate(
            endpoint,
            response_type=ListItemResponse,
            params={"limit": limit},
            max_items=limit if limit > 0 else None,
        )
