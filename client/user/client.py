"""User client for user-specific data."""

from config.endpoints import TRAKT_ENDPOINTS
from models.types import UserWatchedMovie, UserWatchedShow
from utils.api.errors import handle_api_errors

from ..auth import AuthClient


class UserClient(AuthClient):
    """Client for handling user-specific operations that require authentication."""

    @handle_api_errors
    async def get_user_watched_shows(self) -> list[UserWatchedShow]:
        """Get shows watched by the authenticated user.

        Returns:
            List of shows watched by the user
        """
        if not self.is_authenticated():
            return []

        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["user_watched_shows"], response_type=UserWatchedShow
        )

    @handle_api_errors
    async def get_user_watched_movies(self) -> list[UserWatchedMovie]:
        """Get movies watched by the authenticated user.

        Returns:
            List of movies watched by the user
        """
        if not self.is_authenticated():
            return []

        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["user_watched_movies"], response_type=UserWatchedMovie
        )
