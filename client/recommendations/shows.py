"""Client for show recommendations."""

from urllib.parse import quote

from client.auth import AuthClient
from config.api import DEFAULT_LIMIT
from config.endpoints import TRAKT_ENDPOINTS
from models.recommendations.recommendation import TraktRecommendedShow
from utils.api.error_types import AuthenticationRequiredError
from utils.api.errors import handle_api_errors
from utils.api.id_helpers import build_trakt_id_object


class ShowRecommendationsClient(AuthClient):
    """Client for fetching show recommendations from Trakt."""

    @handle_api_errors
    async def get_show_recommendations(
        self,
        limit: int = DEFAULT_LIMIT,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> list[TraktRecommendedShow]:
        """Fetch personalized show recommendations.

        Note: The Trakt recommendations API does not support pagination.
        Use the limit parameter (max 100) to control number of results.

        Args:
            limit: Number of results to return (max 100).
            ignore_collected: Filter out shows user has collected.
            ignore_watchlisted: Filter out shows user has watchlisted.

        Returns:
            List of show recommendations.

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

        return await self._make_typed_list_request(
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
        data = build_trakt_id_object(show_id, "shows")
        await self._post_request(endpoint, data)
        return True
