"""Client for movie recommendations."""

from typing import overload
from urllib.parse import quote

from client.auth import AuthClient
from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.recommendations.recommendation import TraktRecommendedMovie
from models.types.pagination import PaginatedResponse
from utils.api.error_types import AuthenticationRequiredError
from utils.api.errors import handle_api_errors


class MovieRecommendationsClient(AuthClient):
    """Client for fetching movie recommendations from Trakt."""

    @overload
    async def get_movie_recommendations(
        self,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> list[TraktRecommendedMovie]: ...

    @overload
    async def get_movie_recommendations(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int = 1,
        max_pages: int = DEFAULT_MAX_PAGES,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> PaginatedResponse[TraktRecommendedMovie]: ...

    @handle_api_errors
    async def get_movie_recommendations(
        self,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> list[TraktRecommendedMovie] | PaginatedResponse[TraktRecommendedMovie]:
        """Fetch personalized movie recommendations.

        Args:
            limit: Number of results per page (max 100).
            page: Page number. If None, auto-paginates all results.
            max_pages: Maximum pages to fetch when auto-paginating.
            ignore_collected: Filter out movies user has collected.
            ignore_watchlisted: Filter out movies user has watchlisted.

        Returns:
            List of recommendations or paginated response.

        Raises:
            AuthenticationRequiredError: If the client is not authenticated.
        """
        if not self.is_authenticated():
            raise AuthenticationRequiredError("get movie recommendations")

        endpoint = TRAKT_ENDPOINTS["recommendations_movies"]
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
                response_type=TraktRecommendedMovie,
            )

        params["page"] = page
        return await self._make_paginated_request(
            endpoint=endpoint,
            params=params,
            response_type=TraktRecommendedMovie,
        )

    @handle_api_errors
    async def hide_movie_recommendation(self, movie_id: str) -> bool:
        """Hide a movie from future recommendations.

        Args:
            movie_id: Trakt ID, slug, or IMDB ID.

        Returns:
            True if successfully hidden.

        Raises:
            AuthenticationRequiredError: If the client is not authenticated.
        """
        if not self.is_authenticated():
            raise AuthenticationRequiredError("hide movie recommendation")

        endpoint = TRAKT_ENDPOINTS["hide_movie_recommendation"].replace(
            ":id", quote(movie_id, safe="")
        )
        await self._delete_request(endpoint)
        return True

    @handle_api_errors
    async def unhide_movie_recommendation(self, movie_id: str) -> bool:
        """Unhide a movie to restore it in future recommendations.

        Args:
            movie_id: Trakt ID, slug, or IMDB ID.

        Returns:
            True if successfully unhidden.

        Raises:
            AuthenticationRequiredError: If the client is not authenticated.
        """
        if not self.is_authenticated():
            raise AuthenticationRequiredError("unhide movie recommendation")

        endpoint = TRAKT_ENDPOINTS["unhide_recommendations"]

        # Build movie object for API request
        if movie_id.isdigit():
            movie_obj: dict[str, dict[str, str | int]] = {
                "ids": {"trakt": int(movie_id)}
            }
        elif movie_id.startswith("tt"):
            movie_obj = {"ids": {"imdb": movie_id}}
        else:
            movie_obj = {"ids": {"slug": movie_id}}

        data = {"movies": [movie_obj]}
        await self._post_request(endpoint, data)
        return True
