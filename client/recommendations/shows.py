"""Client for show recommendations."""

from typing import overload
from urllib.parse import quote

from client.auth import AuthClient
from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.recommendations.recommendation import TraktRecommendedShow
from models.types.pagination import PaginatedResponse
from utils.api.error_types import AuthenticationRequiredError
from utils.api.errors import handle_api_errors


class ShowRecommendationsClient(AuthClient):
    """Client for fetching show recommendations from Trakt."""

    @overload
    async def get_show_recommendations(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> list[TraktRecommendedShow]: ...

    @overload
    async def get_show_recommendations(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = 1,
        max_pages: int = DEFAULT_MAX_PAGES,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> PaginatedResponse[TraktRecommendedShow]: ...

    @handle_api_errors
    async def get_show_recommendations(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> list[TraktRecommendedShow] | PaginatedResponse[TraktRecommendedShow]:
        """Fetch personalized show recommendations.

        Args:
            limit: Number of results per page (max 100).
            page: Page number. If None, auto-paginates all results.
            max_pages: Maximum pages to fetch when auto-paginating.
            ignore_collected: Filter out shows user has collected.
            ignore_watchlisted: Filter out shows user has watchlisted.

        Returns:
            List of recommendations or paginated response.

        Raises:
            AuthenticationRequiredError: If the client is not authenticated.
        """
        if not self.is_authenticated():
            raise AuthenticationRequiredError("get show recommendations")

        endpoint = TRAKT_ENDPOINTS["recommendations_shows"]
        params: dict[str, str | int | bool] = {"limit": limit}

        if ignore_collected:
            params["ignore_collected"] = "true"
        if ignore_watchlisted:
            params["ignore_watchlisted"] = "true"

        if page is None:
            return await self.auto_paginate(
                endpoint=endpoint,
                params=params,
                max_pages=max_pages,
                response_type=TraktRecommendedShow,
            )

        params["page"] = page
        return await self._make_paginated_request(
            endpoint=endpoint,
            params=params,
            response_type=TraktRecommendedShow,
        )

    @handle_api_errors
    async def hide_show_recommendation(self, show_id: str) -> bool:
        """Hide a show from future recommendations.

        Args:
            show_id: Trakt ID, slug, or IMDB ID.

        Returns:
            True if successfully hidden.

        Raises:
            AuthenticationRequiredError: If the client is not authenticated.
        """
        if not self.is_authenticated():
            raise AuthenticationRequiredError("hide show recommendation")

        endpoint = TRAKT_ENDPOINTS["hide_show_recommendation"].replace(
            ":id", quote(show_id, safe="")
        )
        await self._delete_request(endpoint)
        return True

    @handle_api_errors
    async def unhide_show_recommendation(self, show_id: str) -> bool:
        """Unhide a show to restore it in future recommendations.

        Args:
            show_id: Trakt ID, slug, or IMDB ID.

        Returns:
            True if successfully unhidden.

        Raises:
            AuthenticationRequiredError: If the client is not authenticated.
        """
        if not self.is_authenticated():
            raise AuthenticationRequiredError("unhide show recommendation")

        endpoint = TRAKT_ENDPOINTS["unhide_recommendations"]

        # Build show object for API request
        if show_id.isdigit():
            show_obj: dict[str, dict[str, str | int]] = {"ids": {"trakt": int(show_id)}}
        elif show_id.startswith("tt"):
            show_obj = {"ids": {"imdb": show_id}}
        else:
            show_obj = {"ids": {"slug": show_id}}

        data = {"shows": [show_obj]}
        await self._post_request(endpoint, data)
        return True
