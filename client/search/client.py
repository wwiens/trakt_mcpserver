"""Search client for searching shows and movies."""

from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.types import SearchResult
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class SearchClient(BaseClient):
    """Client for handling search operations."""

    @handle_api_errors
    async def search_shows(
        self, query: str, limit: int = DEFAULT_LIMIT
    ) -> list[SearchResult]:
        """Search for shows on Trakt.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of show search results
        """
        # Construct search endpoint with 'show' type filter
        search_endpoint = f"{TRAKT_ENDPOINTS['search']}/show"

        # Make the search request
        return await self._make_typed_list_request(
            search_endpoint,
            response_type=SearchResult,
            params={"query": query, "limit": limit},
        )

    @handle_api_errors
    async def search_movies(
        self, query: str, limit: int = DEFAULT_LIMIT
    ) -> list[SearchResult]:
        """Search for movies on Trakt."""
        search_endpoint = f"{TRAKT_ENDPOINTS['search']}/movie"
        return await self._make_typed_list_request(
            search_endpoint,
            response_type=SearchResult,
            params={"query": query, "limit": limit},
        )
