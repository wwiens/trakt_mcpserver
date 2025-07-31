"""User client for user-specific data."""

from typing import Any

from config.endpoints import TRAKT_ENDPOINTS
from config.errors import AUTH_REQUIRED
from utils.api.errors import InvalidParamsError, handle_api_errors

from ..auth import AuthClient


class UserClient(AuthClient):
    """Client for handling user-specific operations that require authentication."""

    @handle_api_errors
    async def get_user_watched_shows(self) -> list[dict[str, Any]]:
        """Get shows watched by the authenticated user.

        Returns:
            List of shows watched by the user
        """
        if not self.is_authenticated():
            raise InvalidParamsError(AUTH_REQUIRED)

        return await self._make_list_request(TRAKT_ENDPOINTS["user_watched_shows"])

    @handle_api_errors
    async def get_user_watched_movies(self) -> list[dict[str, Any]]:
        """Get movies watched by the authenticated user.

        Returns:
            List of movies watched by the user
        """
        if not self.is_authenticated():
            raise InvalidParamsError(AUTH_REQUIRED)

        return await self._make_list_request(TRAKT_ENDPOINTS["user_watched_movies"])
