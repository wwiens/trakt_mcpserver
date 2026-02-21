"""Box office movies functionality."""

from config.endpoints import TRAKT_ENDPOINTS
from models.types.api_responses import BoxOfficeMovieWrapper
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class BoxOfficeMoviesClient(BaseClient):
    """Client for box office movies operations."""

    @handle_api_errors
    async def get_boxoffice_movies(self) -> list[BoxOfficeMovieWrapper]:
        """Get the top 10 grossing movies in the U.S. box office last weekend.

        Updated every Monday morning. No pagination — always returns top 10.

        Returns:
            List of box office movies with revenue data
        """
        return await self._make_typed_list_request(
            TRAKT_ENDPOINTS["movies_boxoffice"],
            response_type=BoxOfficeMovieWrapper,
        )
